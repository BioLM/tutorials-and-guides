#!/usr/bin/env python3
"""List and validate algorithm slugs for ALGORITHM_MAP drafts."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REFS_DIR = SCRIPT_DIR.parent / "references"
ALGORITHM_SLUGS_MD = REFS_DIR / "algorithm-slugs.md"

# Embedded slugs (from algorithm-slugs.md / biolm_web ALGORITHM_MAP)
EMBEDDED_SLUGS = {
    "esmfold",
    "esm2-150m",
    "esm2-35m",
    "esm2-650m",
    "esm2-8m",
    "esm1v-all",
    "esm-if1",
    "progen2",
    "biolmtox-v1",
    "antifold",
    "ablang2",
    "igbert-paired",
    "igbert-unpaired",
    "immunefold-antibody",
}

# Stems with known ALGORITHM_MAP entries in biolm_web
EMBEDDED_ALGORITHM_MAP_STEMS = {
    "0_Introduction",
    "1.0_ESMFold",
    "1.1_ESMFold_PDB_Generation",
    "2.0_ESM2",
    "2.1_ESM2_Attention_Map",
    "2.2_ESM2_Protein_Contact_Map",
    "2.3_ESM2_Embeddings_XGBoost",
    "3.0_ESM_1v",
    "3.1_ESM-1v_Deep_Mutational_Scan_Protein",
    "4.0_ESM-IF1",
    "6.0_ProGen2",
    "8.0_BioLMTox_Toxin_Classification",
    "8.1_BioLMTox_Toxin_Similarity",
    "9.0_Generation_for_Antibody_Engineering",
    "9.1_Intrinsic_Scoring_for_Antibody_Engineering",
    "9.2_Structural_Scoring_for_Antibody_Engineering",
    "9.3_Downstream_for_Antibody_Engineering",
}


def parse_algorithm_map_from_biolm_web(root: Path) -> tuple[set[str], dict[str, list[str]]]:
    """Parse ALGORITHM_MAP slugs and stem keys from biolm_web generate script."""
    script = root / "scripts" / "generate_jupyter_migration.py"
    if not script.exists():
        return set(), {}
    text = script.read_text(encoding="utf-8")
    slugs: set[str] = set()
    stem_map: dict[str, list[str]] = {}
    # Match "stem": ["slug1", "slug2"]
    for match in re.finditer(
        r'"([^"]+)":\s*\[([^\]]*)\]', text.split("ALGORITHM_MAP", 1)[-1]
    ):
        stem = match.group(1)
        inner = match.group(2)
        entries = re.findall(r'"([^"]+)"', inner)
        stem_map[stem] = entries
        slugs.update(entries)
    return slugs, stem_map


def load_slugs() -> set[str]:
    slugs = set(EMBEDDED_SLUGS)
    biolm_root = os.environ.get("BIOLM_WEB_ROOT")
    if biolm_root:
        extra, _ = parse_algorithm_map_from_biolm_web(Path(biolm_root))
        slugs.update(extra)
    return slugs


def load_algorithm_map_stems() -> set[str]:
    stems = set(EMBEDDED_ALGORITHM_MAP_STEMS)
    biolm_root = os.environ.get("BIOLM_WEB_ROOT")
    if biolm_root:
        _, stem_map = parse_algorithm_map_from_biolm_web(Path(biolm_root))
        stems.update(stem_map.keys())
    return stems


def validate_slugs(requested: list[str]) -> tuple[list[str], list[str]]:
    known = load_slugs()
    valid = [s for s in requested if s in known]
    unknown = [s for s in requested if s not in known]
    return valid, unknown


def main() -> int:
    parser = argparse.ArgumentParser(description="List/validate algorithm slugs")
    parser.add_argument("--list", action="store_true", help="List all known slugs")
    parser.add_argument(
        "--list-stems",
        action="store_true",
        help="List notebook stems in ALGORITHM_MAP",
    )
    parser.add_argument(
        "--validate",
        nargs="+",
        metavar="SLUG",
        help="Validate slug(s) against known list",
    )
    parser.add_argument(
        "--stem-mapped",
        metavar="STEM",
        help="Check if notebook stem has ALGORITHM_MAP entry",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.list:
        slugs = sorted(load_slugs())
        if args.json:
            print(json.dumps(slugs, indent=2))
        else:
            for s in slugs:
                print(s)
        return 0

    if args.list_stems:
        stems = sorted(load_algorithm_map_stems())
        if args.json:
            print(json.dumps(stems, indent=2))
        else:
            for s in stems:
                print(s)
        return 0

    if args.validate:
        valid, unknown = validate_slugs(args.validate)
        result = {"valid": valid, "unknown": unknown}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for s in valid:
                print(f"OK: {s}")
            for s in unknown:
                print(f"UNKNOWN: {s}")
        return 1 if unknown else 0

    if args.stem_mapped:
        stems = load_algorithm_map_stems()
        mapped = args.stem_mapped in stems
        if args.json:
            print(json.dumps({"stem": args.stem_mapped, "mapped": mapped}))
        else:
            status = "yes" if mapped else "no"
            print(f"ALGORITHM_MAP entry for {args.stem_mapped}: {status}")
        return 0 if mapped else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
