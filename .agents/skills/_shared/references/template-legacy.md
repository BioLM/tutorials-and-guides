# Legacy notebook template

Reference: `content/0_Introduction.ipynb`, `content/2.0_ESM2.ipynb`

Use when the user explicitly chooses the legacy template.

## Cell order (minimal)

| # | Type | Content |
|---|------|---------|
| 0 | markdown | BioLM header HTML + `# {Title}` + description + header table + `---` |
| 1 | markdown | Brief intro (auth note, context) |
| 2 | code | `import os` + commented token line: `# os.environ['BIOLM_TOKEN'] = "Your token here"` |
| 3+ | markdown/code | Content sections |

## Differences from modern template

- No required `learn-cell` or Requirements block
- No required token guard (`raise EnvironmentError`); commented assignment is acceptable
- No required Next Steps footer
- May have committed cell outputs (discouraged for new guides but tolerated)

## Header HTML

Same BioLM header structure as modern template (`jupyter-biolm-header`, header table).

## When to use

- User explicitly requests legacy template
- Extending an older series (0–9.x) where siblings use legacy format
- Agent should still ask modern vs legacy unless user specifies upfront
