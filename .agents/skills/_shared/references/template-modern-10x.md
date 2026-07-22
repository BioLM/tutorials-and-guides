# Modern (10.x) notebook template

Gold standard: `content/10.0_Screen_1000_Peptides.ipynb`

Scaffold with cleared outputs (`execution_count: null`, empty `outputs`). Use nbformat 4, nbformat_minor 5.

## Cell order

| # | Type | id | Content |
|---|------|-----|---------|
| 0 | markdown | — | BioLM header HTML + `# {Title}` + one-line description + header table + `---` |
| 1 | markdown | — | *(optional)* Preview callout if using unreleased SDK features |
| 2 | markdown | `learn-cell` | **What you'll learn:** bullets + **Requirements:** fenced block with pip install + `export BIOLM_TOKEN=...` |
| 3 | markdown | — | `## Setup` |
| 4 | code | — | imports + `BIOLM_TOKEN` / credentials guard (see below) |
| 5+ | markdown/code | — | Content sections (`## ...`) |
| last | markdown | — | Next Steps footer (see below) |

## Header HTML (cell 0)

Include:
- `<div class="jupyter-biolm-header">` with BioLM logo
- H1 title matching predicted `display_name` from filename
- One-line description paragraph
- `<table class="jupyter-biolm-header-table">` with Postman + Python SDK doc links
- Horizontal rule `---`

## Preview callout (optional cell 1)

```markdown
> **⚠️ Preview Feature** — The `biolm.pipeline` module used in this guide is currently in preview...
```

## Token guard (Setup code cell)

```python
import os
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

## Next Steps footer (final markdown cell)

Must include:
- Links to jupyter.biolm.ai and docs.biolm.ai
- BioLM Console Catalog link
- Catalog table with enzyme/antibody/biosecurity/etc. icons
- Contact us link

Copy structure from `10.0_Screen_1000_Peptides.ipynb` cell 14.

## Metadata

```json
{
  "kernelspec": {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
  },
  "language_info": {
    "name": "python",
    "version": "3.10.0"
  }
}
```
