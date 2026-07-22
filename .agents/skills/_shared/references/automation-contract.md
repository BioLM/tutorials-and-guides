# Cross-repo automation contract (reference only)

These skills **do not run** conversion or biolm_web processes. This document describes what happens after merge so authors and reviewers can validate repo contents.

## tutorials-and-guides (source of truth)

| Path | Purpose |
|------|---------|
| `content/*.ipynb` | Notebook source (flat directory) |
| `css/custom.css` | Injected into converted HTML on sync |
| `content/data/...` | Data shipped with guides |
| `requirements.txt` | Runtime dependencies for execution tests |

On push to `main` when `content/*.ipynb` changes, [`.github/workflows/notify-notebook-sync.yml`](../../../.github/workflows/notify-notebook-sync.yml) dispatches `notebook-sync` to biolm_web with `{ filename, change_type }` and `source_sha`.

## biolm_web (ingestion — manual / automated elsewhere)

1. `handle-notebook-sync.yml` checks out **all** notebooks from tutorials-and-guides `main`.
2. `scripts/convert_notebooks_to_html.py` → `jupyter_html/{stem}.html`
3. `scripts/generate_jupyter_migration.py` → Django migration for `JupyterPage` records
4. Served at `biolm.ai/guides/{slug}/` via `JupyterSolution` view
5. HTML embedded via `ui/templates/sphinx_builds/` → symlink to `jupyter_html/`

## Derived fields (from filename stem)

- **slug:** strip leading `N.N_` prefix, underscores → hyphens, lowercase
- **display_name:** strip prefix, underscores → spaces, title case
- **jupyter_html_fname:** `{stem}.html`
- **description:** empty in auto-migration until set in Django admin

## Manual follow-up in biolm_web

- Add stem to `ALGORITHM_MAP` in `scripts/generate_jupyter_migration.py` for model badge links on guide pages
- Optionally set `description`, `docs_url`, etc. in Django admin

## JupyterLite (separate deploy)

- [`deploy.yml`](../../../.github/workflows/deploy.yml) runs `jupyter lite build --contents content`
- "Try in Notebook" links use exact filename: `?path={stem}.ipynb`
