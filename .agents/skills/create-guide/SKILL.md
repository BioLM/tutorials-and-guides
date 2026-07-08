---
name: create-guide
description: >-
  Create a new BioLM tutorial notebook in content/. Runs an interactive
  questionnaire, proposes filename and site metadata for user confirmation,
  scaffolds from modern (10.x) or legacy template, drafts biolm_web ALGORITHM_MAP
  entries, and offers requirements.txt updates. Use when adding a new guide,
  tutorial, or notebook to tutorials-and-guides.
---

# Create Guide

Create a new tutorial notebook in `content/` following repo conventions and biolm_web ingestion rules.

**Out of scope:** HTML conversion, JupyterLite build, biolm_web sync — never run those.

## References

Read before scaffolding:

- [`../_shared/references/guide-conventions.md`](../_shared/references/guide-conventions.md)
- [`../_shared/references/automation-contract.md`](../_shared/references/automation-contract.md)
- [`../_shared/references/template-modern-10x.md`](../_shared/references/template-modern-10x.md) — default
- [`../_shared/references/template-legacy.md`](../_shared/references/template-legacy.md)
- Gold standard modern: `content/10.0_Screen_1000_Peptides.ipynb`

## Phase A — Interactive questionnaire

Use AskQuestion when available; otherwise ask conversationally. Do not skip questions unless the user already answered them.

1. **Series** — e.g. `10` (pipeline), `9` (antibody), `0` (intro)
2. **Working title** — human-readable topic
3. **Template** — always ask: **modern** (10.x default) vs **legacy**
4. **Learning objectives** — bullets for learn-cell (modern only)
5. **Models/APIs** — for Requirements block and ALGORITHM_MAP draft
6. **Preview feature?** — needs `biolm-sdk[pipeline]` / `biolm.pipeline` callout?
7. **Data files** — new CSV/PDB under `content/data/...`?
8. **Execution profile** — API-heavy / expected runtime (informational)

Suggest next filename number:

```bash
python .agents/skills/_shared/scripts/predict_metadata.py --next-in-series 10
```

## Phase B — Propose and confirm (before any file write)

Build stem from series + subseries + title, then check collisions:

```bash
python .agents/skills/_shared/scripts/predict_metadata.py --from-title 10 7 "My New Guide"
python .agents/skills/_shared/scripts/predict_metadata.py --check-collisions 10.7_My_New_Guide --json
```

Present to user:

```
Proposed filename:  10.7_My_New_Guide.ipynb
Site slug:          my-new-guide → biolm.ai/guides/my-new-guide/
Display name:       My New Guide
JupyterLite path:   ?path=10.7_My_New_Guide.ipynb
Collisions:         none / CONFLICT ...
```

**Stop and wait for explicit user confirmation** before writing files. If collisions exist, suggest alternatives.

## Phase C — Scaffold

After confirmation:

1. Write `content/{filename}.ipynb` per chosen template
2. **Modern:** header, optional preview callout, learn-cell (`id: learn-cell`), Setup + token guard, content sections, Next Steps footer
3. **Legacy:** header, intro, commented token line, content sections
4. H1 must align with predicted `display_name`
5. Cleared outputs (`execution_count: null`, empty `outputs`)
6. Add data files under `content/data/...` if requested

### Token guard (modern Setup cell)

```python
from pathlib import Path

TOKEN = os.environ.get("BIOLM_TOKEN") or os.environ.get("BIOLMAI_TOKEN", "")
if not TOKEN:
    creds = Path.home() / ".biolm" / "credentials"
    legacy = Path.home() / ".biolmai" / "credentials"
    if not creds.exists() and not legacy.exists():
        raise EnvironmentError(
            "Set BIOLM_TOKEN before running, or run `biolm login`.\n"
            "Get a token at https://biolm.ai/ui/accounts/user-api-tokens/"
        )
```

## Phase D — Post-scaffold offers

### requirements.txt

Compare learn-cell Requirements against [`requirements.txt`](../../requirements.txt). **Offer** to add missing packages — do not add silently.

### ALGORITHM_MAP draft

If models/APIs were specified, validate slugs and output a draft for the user to paste into biolm_web:

```bash
python .agents/skills/_shared/scripts/list_algorithm_slugs.py --validate esm2-650m biolmtox-v1
```

```python
# Add to biolm_web/scripts/generate_jupyter_migration.py ALGORITHM_MAP
"10.7_My_New_Guide": ["esm2-650m"],
```

Warn on unknown slugs. User applies this change in biolm_web separately.

## Phase E — Handoff

Remind user to run **test-guides** on the new notebook before opening a PR:

```bash
export BIOLM_TOKEN=your-token
.agents/skills/test-guides/scripts/run-notebook.sh content/10.7_My_New_Guide.ipynb
```

Optionally suggest **review-guides** for static checks:

```bash
python .agents/skills/review-guides/scripts/review.py content/10.7_My_New_Guide.ipynb
```
