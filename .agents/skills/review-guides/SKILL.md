---
name: review-guides
description: >-
  Review notebook structure, naming, formatting, and supporting files against
  repo conventions and biolm_web ingestion requirements. Static checks only —
  no execution or HTML conversion. Use before PRs or when validating guides
  will work with cross-repo automation.
paths: content/**
---

# Review Guides

Static sanity checks on `content/*.ipynb` and supporting files. Validates repo layout and biolm_web ingestion rules **without running conversion or execution**.

## Out of scope (never run)

- HTML conversion
- biolm_web sync scripts
- `jupyter nbconvert --execute`
- `jupyter lite build`

## Run review

All notebooks:

```bash
python .agents/skills/review-guides/scripts/review.py
```

Subset by glob:

```bash
python .agents/skills/review-guides/scripts/review.py 10.*
python .agents/skills/review-guides/scripts/review.py content/10.0_Screen_1000_Peptides.ipynb
```

JSON output:

```bash
python .agents/skills/review-guides/scripts/review.py --json
```

Exit code 1 if any **fail**-severity issues.

## Check profiles

Each notebook is tagged **modern** (10.x or has `learn-cell`) or **legacy**.

### Universal (fail) — all notebooks

- Located directly under `content/*.ipynb`
- Valid nbformat 4 JSON
- Filename matches convention
- No slug / display_name collisions across the set
- Referenced `data/...` paths exist under `content/`
- No hardcoded `BIOLM_TOKEN` / `BIOLMAI_TOKEN` literals

### Modern profile (fail)

- `jupyter-biolm-header` in content
- H1 title present (warn if differs from filename-derived display_name)
- `learn-cell` with Requirements block
- Token guard (`EnvironmentError` on missing token)
- Next Steps footer

### Legacy profile (fail / warn)

- BioLM header present
- H1 warn if missing

### Automation (warn / info)

- Stem missing from ALGORITHM_MAP when models are referenced
- Site description empty until Django admin (info)
- Predicted guides URL after merge (info)

## Metadata helpers

Preview slug/display_name for a filename:

```bash
python .agents/skills/_shared/scripts/predict_metadata.py 10.7_My_Guide.ipynb
```

Check ALGORITHM_MAP coverage:

```bash
python .agents/skills/_shared/scripts/list_algorithm_slugs.py --stem-mapped 10.0_Screen_1000_Peptides
```

## References

- [`../_shared/references/guide-conventions.md`](../_shared/references/guide-conventions.md)
- [`../_shared/references/automation-contract.md`](../_shared/references/automation-contract.md)
- [`../_shared/references/algorithm-slugs.md`](../_shared/references/algorithm-slugs.md)

## Expected first-run behavior

Legacy notebooks (0–9.x) may report many modern-template failures if mis-detected. Review output separates **fail** vs **warn** for triage. Use glob to focus on new/changed guides during development.
