#!/usr/bin/env python3
"""Predict site metadata from notebook filename stems.

Mirrors biolm_web/scripts/generate_jupyter_migration.py logic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
CONTENT_DIR = REPO_ROOT / "content"

FILENAME_PATTERN = re.compile(
    r"^(?:\d+(?:\.\d+)?_\w+|0_\w+|[\w.-]+)\.ipynb$",
    re.IGNORECASE,
)


def filename_to_slug(stem: str) -> str:
    clean = re.sub(r"^\d+(?:[._]\d+)?[._]", "", stem)
    slug = re.sub(r"[_\s]+", "-", clean).lower()
    slug = re.sub(r"[^a-z0-9-]", "", slug).strip("-")
    return slug or re.sub(r"[^a-z0-9-]", "", stem.lower())


def filename_to_display_name(stem: str) -> str:
    clean = re.sub(r"^\d+(?:[._]\d+)?[._]", "", stem)
    return clean.replace("_", " ").replace("-", " ").title()


def stem_from_arg(name: str) -> str:
    path = Path(name)
    if path.suffix == ".ipynb":
        return path.stem
    return name.replace(".ipynb", "")


def title_to_stem(series: str, subseries: int, title: str) -> str:
    """Build filename stem from series, subseries, and human title."""
    words = re.sub(r"[^a-zA-Z0-9\s]", "", title).split()
    title_part = "_".join(words) if words else "Untitled"
    if subseries is not None:
        return f"{series}.{subseries}_{title_part}"
    return f"{series}_{title_part}"


def list_notebook_stems(content_dir: Path = CONTENT_DIR) -> list[str]:
    return sorted(p.stem for p in content_dir.glob("*.ipynb"))


def next_in_series(series: str, content_dir: Path = CONTENT_DIR) -> int:
    """Return next available subseries number for e.g. series '10' -> 10.7."""
    prefix = f"{series}."
    used: list[int] = []
    for stem in list_notebook_stems(content_dir):
        if stem.startswith(prefix):
            rest = stem[len(prefix) :]
            num_match = re.match(r"^(\d+)_", rest)
            if num_match:
                used.append(int(num_match.group(1)))
    return max(used, default=-1) + 1


def predict_metadata(stem: str) -> dict:
    return {
        "stem": stem,
        "filename": f"{stem}.ipynb",
        "slug": filename_to_slug(stem),
        "display_name": filename_to_display_name(stem),
        "html_fname": f"{stem}.html",
        "jupyterlite_path": f"?path={stem}.ipynb",
        "guides_url": f"https://biolm.ai/guides/{filename_to_slug(stem)}/",
    }


def check_collisions(stem: str, content_dir: Path = CONTENT_DIR) -> dict:
    meta = predict_metadata(stem)
    collisions: list[str] = []
    existing = list_notebook_stems(content_dir)

    if stem in existing:
        collisions.append(f"stem '{stem}' already exists")

    for other in existing:
        if other == stem:
            continue
        other_meta = predict_metadata(other)
        if meta["slug"] == other_meta["slug"]:
            collisions.append(f"slug '{meta['slug']}' conflicts with {other}.ipynb")
        if meta["display_name"] == other_meta["display_name"]:
            collisions.append(
                f"display_name '{meta['display_name']}' conflicts with {other}.ipynb"
            )
        if meta["html_fname"] == other_meta["html_fname"]:
            collisions.append(
                f"html_fname '{meta['html_fname']}' conflicts with {other}.ipynb"
            )

    return {"metadata": meta, "collisions": collisions}


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict notebook site metadata")
    parser.add_argument(
        "name",
        nargs="?",
        help="Notebook filename or stem (e.g. 10.7_My_Guide.ipynb)",
    )
    parser.add_argument(
        "--next-in-series",
        metavar="N",
        help="Suggest next subseries number for series N (e.g. 10)",
    )
    parser.add_argument(
        "--from-title",
        nargs=3,
        metavar=("SERIES", "SUBSERIES", "TITLE"),
        help="Build stem from series, subseries, title",
    )
    parser.add_argument(
        "--check-collisions",
        metavar="STEM",
        help="Check stem for collisions against content/",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.next_in_series:
        n = next_in_series(args.next_in_series)
        result = {"series": args.next_in_series, "next_subseries": n}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Next subseries for {args.next_in_series}.x: {args.next_in_series}.{n}")
        return 0

    if args.from_title:
        series, subseries_str, title = args.from_title
        stem = title_to_stem(series, int(subseries_str), title)
        result = check_collisions(stem)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_metadata(result)
        return 1 if result["collisions"] else 0

    if args.check_collisions:
        result = check_collisions(stem_from_arg(args.check_collisions))
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_metadata(result)
        return 1 if result["collisions"] else 0

    if not args.name:
        parser.print_help()
        return 1

    stem = stem_from_arg(args.name)
    meta = predict_metadata(stem)
    if args.json:
        print(json.dumps(meta, indent=2))
    else:
        print(f"Stem:         {meta['stem']}")
        print(f"Filename:     {meta['filename']}")
        print(f"Slug:         {meta['slug']}")
        print(f"Display name: {meta['display_name']}")
        print(f"HTML file:    {meta['html_fname']}")
        print(f"Guides URL:   {meta['guides_url']}")
        print(f"JupyterLite:  jupyter.biolm.ai/lab{meta['jupyterlite_path']}")
    return 0


def _print_metadata(result: dict) -> None:
    meta = result["metadata"]
    print(f"Proposed filename:  {meta['filename']}")
    print(f"Site slug:          {meta['slug']} → {meta['guides_url']}")
    print(f"Display name:       {meta['display_name']}")
    print(f"JupyterLite path:   {meta['jupyterlite_path']}")
    if result["collisions"]:
        print("Collisions:")
        for c in result["collisions"]:
            print(f"  - {c}")
    else:
        print("Collisions:         none")


if __name__ == "__main__":
    sys.exit(main())
