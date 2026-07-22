#!/usr/bin/env python3
"""Static review of tutorial notebooks in content/. No execution or conversion."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SHARED_SCRIPTS = SCRIPT_DIR.parent.parent / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from list_algorithm_slugs import load_algorithm_map_stems  # noqa: E402
from predict_metadata import (  # noqa: E402
    filename_to_display_name,
    filename_to_slug,
    list_notebook_stems,
    predict_metadata,
)

REPO_ROOT = SCRIPT_DIR.parents[3]
CONTENT_DIR = REPO_ROOT / "content"

FILENAME_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)?_\w+|0_\w+|[A-Za-z0-9][\w.-]*)\.ipynb$"
)

HARDCODED_TOKEN = re.compile(
    r"""BIOLM(?:AI)?_TOKEN\s*=\s*['"][^'"]+['"]""",
    re.IGNORECASE,
)

DATA_PATH = re.compile(
    r"""['"](data/[^'"]+)['"]|open\s*\(\s*['"](data/[^'"]+)['"]""",
)


@dataclass
class Issue:
    severity: str  # fail, warn, info
    check: str
    message: str


@dataclass
class NotebookReport:
    path: str
    stem: str
    profile: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def fail_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "fail")

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warn")


def detect_profile(stem: str, nb: dict) -> str:
    if stem.startswith("10."):
        return "modern"
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown" and cell.get("id") == "learn-cell":
            return "modern"
    return "legacy"


def cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src or ""


def all_sources(nb: dict) -> str:
    return "\n".join(cell_source(c) for c in nb.get("cells", []))


def extract_h1(nb: dict) -> str | None:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        for line in cell_source(cell).splitlines():
            stripped = line.strip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                return stripped[2:].strip()
    return None


def output_size_bytes(nb: dict) -> int:
    total = 0
    for cell in nb.get("cells", []):
        for out in cell.get("outputs", []) or []:
            total += len(json.dumps(out))
    return total


def load_notebook(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"_error": str(e)}


def check_universal(
    path: Path, nb: dict, stem: str, all_stems: list[str]
) -> list[Issue]:
    issues: list[Issue] = []

    if "_error" in nb:
        issues.append(Issue("fail", "valid_json", f"Invalid JSON: {nb['_error']}"))
        return issues

    if path.parent.resolve() != CONTENT_DIR.resolve():
        issues.append(
            Issue("fail", "location", f"Must be directly under content/: {path}")
        )

    if not FILENAME_PATTERN.match(path.name):
        issues.append(
            Issue("fail", "filename_pattern", f"Filename does not match convention: {path.name}")
        )

    if nb.get("nbformat") != 4:
        issues.append(
            Issue("fail", "nbformat", f"Expected nbformat 4, got {nb.get('nbformat')}")
        )

    minor = nb.get("nbformat_minor")
    if minor is not None and minor > 5:
        issues.append(Issue("warn", "nbformat_minor", f"Unusual nbformat_minor: {minor}"))

    meta = predict_metadata(stem)
    for other in all_stems:
        if other == stem:
            continue
        other_meta = predict_metadata(other)
        if meta["slug"] == other_meta["slug"]:
            issues.append(
                Issue(
                    "fail",
                    "slug_collision",
                    f"Slug '{meta['slug']}' conflicts with {other}.ipynb",
                )
            )
        if meta["display_name"] == other_meta["display_name"]:
            issues.append(
                Issue(
                    "fail",
                    "display_name_collision",
                    f"display_name '{meta['display_name']}' conflicts with {other}.ipynb",
                )
            )

    combined = all_sources(nb)
    if HARDCODED_TOKEN.search(combined):
        issues.append(
            Issue("fail", "hardcoded_token", "Hardcoded BIOLM_TOKEN assignment found")
        )

    for match in DATA_PATH.finditer(combined):
        rel = match.group(1) or match.group(2)
        if rel and not (CONTENT_DIR / rel).exists():
            issues.append(
                Issue("fail", "missing_data", f"Referenced data file not found: {rel}")
            )

    return issues


def check_modern(nb: dict, stem: str) -> list[Issue]:
    issues: list[Issue] = []
    combined = all_sources(nb)

    if "jupyter-biolm-header" not in combined:
        issues.append(Issue("fail", "biolm_header", "Missing jupyter-biolm-header HTML"))

    h1 = extract_h1(nb)
    if not h1:
        issues.append(Issue("fail", "h1_title", "Missing H1 title in markdown"))
    else:
        expected = filename_to_display_name(stem)
        if h1.lower() != expected.lower():
            issues.append(
                Issue(
                    "warn",
                    "h1_display_name",
                    f"H1 '{h1}' differs from filename display_name '{expected}'",
                )
            )

    has_learn = any(
        c.get("cell_type") == "markdown" and c.get("id") == "learn-cell"
        for c in nb.get("cells", [])
    )
    if not has_learn:
        issues.append(Issue("fail", "learn_cell", "Missing learn-cell markdown cell"))
    elif "Requirements:" not in combined and "**Requirements:**" not in combined:
        issues.append(Issue("fail", "requirements_block", "learn-cell missing Requirements block"))

    if ("BIOLM_TOKEN" not in combined and "BIOLMAI_TOKEN" not in combined) or "EnvironmentError" not in combined:
        issues.append(
            Issue("fail", "token_guard", "Missing BIOLM_TOKEN guard (EnvironmentError)")
        )

    if "Next Steps" not in combined:
        issues.append(Issue("fail", "next_steps", "Missing Next Steps footer"))

    if "jupyter.biolm.ai" not in combined:
        issues.append(Issue("warn", "next_steps_links", "Next Steps missing jupyter.biolm.ai link"))

    size = output_size_bytes(nb)
    if size > 100_000:
        issues.append(
            Issue("warn", "large_outputs", f"Large committed outputs (~{size // 1024} KB)")
        )
    elif size > 0:
        for cell in nb.get("cells", []):
            if cell.get("outputs"):
                issues.append(
                    Issue("warn", "committed_outputs", "Notebook has committed cell outputs")
                )
                break

    return issues


def check_legacy(nb: dict) -> list[Issue]:
    issues: list[Issue] = []
    combined = all_sources(nb)

    if "jupyter-biolm-header" not in combined:
        issues.append(Issue("fail", "biolm_header", "Missing jupyter-biolm-header HTML"))

    if not nb.get("cells"):
        issues.append(Issue("fail", "structure", "Notebook has no cells"))

    h1 = extract_h1(nb)
    if not h1:
        issues.append(Issue("warn", "h1_title", "Missing H1 title"))

    return issues


def check_automation(stem: str, nb: dict, profile: str) -> list[Issue]:
    issues: list[Issue] = []
    combined = all_sources(nb).lower()
    mapped_stems = load_algorithm_map_stems()

    model_hints = (
        "esmfold",
        "esm2",
        "esm1v",
        "progen2",
        "biolmtox",
        "antifold",
        "biolm.pipeline",
        "biolm-sdk",
        "biolmai.pipeline",
        "biolmai",
        "biolm",
    )
    references_models = any(h in combined for h in model_hints)

    if references_models and stem not in mapped_stems:
        issues.append(
            Issue(
                "warn",
                "algorithm_map",
                f"Stem '{stem}' not in ALGORITHM_MAP — no model badges on guide page until biolm_web updated",
            )
        )

    issues.append(
        Issue(
            "info",
            "site_description",
            "Auto-sync sets empty description on site until Django admin edit",
        )
    )

    slug = filename_to_slug(stem)
    issues.append(
        Issue(
            "info",
            "guides_url",
            f"After merge to main: biolm.ai/guides/{slug}/",
        )
    )

    return issues


def review_notebook(path: Path, all_stems: list[str]) -> NotebookReport:
    stem = path.stem
    nb = load_notebook(path)
    if nb is None:
        return NotebookReport(str(path), stem, "unknown", [Issue("fail", "load", "Could not load")])

    profile = detect_profile(stem, nb) if "_error" not in nb else "unknown"
    report = NotebookReport(str(path.relative_to(REPO_ROOT)), stem, profile)

    if "_error" in nb:
        report.issues = check_universal(path, nb, stem, all_stems)
        return report

    report.issues.extend(check_universal(path, nb, stem, all_stems))

    if profile == "modern":
        report.issues.extend(check_modern(nb, stem))
    else:
        report.issues.extend(check_legacy(nb))

    report.issues.extend(check_automation(stem, nb, profile))
    return report


def collect_notebooks(patterns: list[str] | None) -> list[Path]:
    all_nbs = sorted(CONTENT_DIR.glob("*.ipynb"))
    if not patterns:
        return all_nbs
    selected: list[Path] = []
    for pat in patterns:
        if pat.endswith(".ipynb"):
            p = CONTENT_DIR / Path(pat).name
            if p.exists():
                selected.append(p)
            else:
                p2 = REPO_ROOT / pat
                if p2.exists():
                    selected.append(p2)
        else:
            glob_pat = pat if pat.endswith(".ipynb") else f"{pat}.ipynb"
            for p in all_nbs:
                if fnmatch(p.name, glob_pat) and p not in selected:
                    selected.append(p)
    return sorted(selected)


def print_report(reports: list[NotebookReport], as_json: bool) -> None:
    if as_json:
        data = [
            {
                "path": r.path,
                "stem": r.stem,
                "profile": r.profile,
                "fail_count": r.fail_count,
                "warn_count": r.warn_count,
                "issues": [
                    {"severity": i.severity, "check": i.check, "message": i.message}
                    for i in r.issues
                ],
            }
            for r in reports
        ]
        print(json.dumps(data, indent=2))
        return

    total_fail = sum(r.fail_count for r in reports)
    total_warn = sum(r.warn_count for r in reports)

    for r in reports:
        icon = "FAIL" if r.fail_count else ("WARN" if r.warn_count else "OK")
        print(f"\n[{icon}] {r.path} (profile: {r.profile})")
        for i in r.issues:
            prefix = i.severity.upper()
            print(f"  {prefix}: [{i.check}] {i.message}")

    print(f"\n--- Summary: {len(reports)} notebook(s), {total_fail} fail(s), {total_warn} warn(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Static review of content/*.ipynb")
    parser.add_argument(
        "patterns",
        nargs="*",
        help="Glob patterns (e.g. 10.*) or paths; default all",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    notebooks = collect_notebooks(args.patterns or None)
    if not notebooks:
        print("No notebooks matched.", file=sys.stderr)
        return 1

    all_stems = list_notebook_stems(CONTENT_DIR)
    reports = [review_notebook(p, all_stems) for p in notebooks]
    print_report(reports, args.json)

    if any(r.fail_count for r in reports):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
