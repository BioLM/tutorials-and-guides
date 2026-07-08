---
name: test-guides
description: >-
  Execute one or more tutorial notebooks from content/ in isolated temporary
  virtual environments to verify they run successfully. Requires BIOLM_TOKEN
  (or BIOLMAI_TOKEN / biolm login credentials). Use when testing guides,
  validating notebook execution, or before opening a PR.
---

# Test Guides

Execute notebook(s) end-to-end in a disposable venv. Validates runtime behavior against the live BioLM API.

## Out of scope (never run)

- HTML conversion (`convert_notebooks_to_html.py`)
- biolm_web sync scripts or processes
- `jupyter lite build`

## Prerequisites

```bash
export BIOLM_TOKEN=your-token-here
# Get one at https://biolm.ai/ui/accounts/user-api-tokens/
# Or: biolm login  (OAuth credentials under ~/.biolm/)
```

Scripts fail fast if neither `BIOLM_TOKEN` / `BIOLMAI_TOKEN` nor credentials file is available.

## Run a single notebook

```bash
.agents/skills/test-guides/scripts/run-notebook.sh content/10.0_Screen_1000_Peptides.ipynb
```

Optional timeout (seconds, default 600):

```bash
.agents/skills/test-guides/scripts/run-notebook.sh content/10.0_Screen_1000_Peptides.ipynb 900
```

## Run multiple notebooks

```bash
# Glob pattern (relative to content/)
.agents/skills/test-guides/scripts/run-notebooks.sh "10.*"

# All notebooks
.agents/skills/test-guides/scripts/run-notebooks.sh --all
```

## What the scripts do

1. Create temp directory + `python3 -m venv`
2. `pip install -r requirements.txt`
3. Execute from `content/` so `data/...` paths resolve
4. `jupyter nbconvert --to notebook --execute` with output to `/tmp/{stem}-executed.ipynb`
5. Tear down venv on exit
6. **Never overwrite** committed notebooks in the repo

## Interpreting failures

| Symptom | Likely cause |
|---------|----------------|
| `BIOLM_TOKEN` error | Token not exported and no `biolm login` credentials |
| `FileNotFoundError` for `data/...` | Missing data file under `content/data/` |
| API / HTTP errors | Invalid token, model access, or rate limits |
| Timeout | Increase second argument; notebook may be API-heavy |
| ImportError | Missing package in `requirements.txt` |

Suggest fixes and re-run after corrections.

## References

- [`../_shared/references/guide-conventions.md`](../_shared/references/guide-conventions.md)
- Root [`requirements.txt`](../../requirements.txt)
