# Guide conventions (tutorials-and-guides)

## Location and naming

- All notebooks live **flat** under `content/*.ipynb` (not in subdirectories).
- Filename pattern: `{series}[.{subseries}]_{Title_In_Snake_Case}.ipynb`
  - Examples: `10.0_Screen_1000_Peptides.ipynb`, `0_Introduction.ipynb`, `2.1_ESM2_Attention_Map.ipynb`
- The filename stem is the **stable ID** across repos and automation.
- Data files go under `content/data/...` and are referenced with paths relative to `content/` (e.g. `data/protein/data/PLA2.csv`).

## Derived site metadata (from filename stem)

Logic mirrors `biolm_web/scripts/generate_jupyter_migration.py`:

| Field | Example (`10.7_My_New_Guide`) |
|-------|-------------------------------|
| HTML file | `10.7_My_New_Guide.html` |
| Site slug | `my-new-guide` → `biolm.ai/guides/my-new-guide/` |
| Display name | `My New Guide` (DB page title) |
| JupyterLite | `jupyter.biolm.ai/lab?path=10.7_My_New_Guide.ipynb` |

Run `python .agents/skills/_shared/scripts/predict_metadata.py STEM` to preview.

## Dependencies

- Root [`requirements.txt`](../../../requirements.txt) is canonical for CI and test execution.
- Modern guides document pip extras in the learn-cell **Requirements** block; offer to add missing packages to `requirements.txt`.

## Styling

- BioLM header HTML uses classes `jupyter-biolm-header` and `jupyter-biolm-header-table`.
- Site conversion injects [`css/custom.css`](../../../css/custom.css) — keep header markup compatible.

## Security

- Never hardcode API tokens. Use `BIOLM_TOKEN` from the environment (legacy `BIOLMAI_TOKEN` still accepted).
- Modern template uses an explicit token / credentials guard in the Setup cell.
- Install the SDK with `pip install biolm-sdk` (or TestPyPI while 1.0 is pre-release):  
  `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ biolm-sdk`  
  Pipeline guides: `"biolm-sdk[pipeline]"`.

## Templates

- **Modern (10.x default):** see [template-modern-10x.md](template-modern-10x.md); gold standard: `content/10.0_Screen_1000_Peptides.ipynb`
- **Legacy:** see [template-legacy.md](template-legacy.md); reference: `content/0_Introduction.ipynb`

## Out of scope for these skills

- HTML conversion, JupyterLite build, biolm_web sync scripts — handled by separate automation.
