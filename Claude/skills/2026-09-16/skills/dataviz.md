# Dataviz

- Slug: `dataviz`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: creating any chart, graph, plot, or dashboard in any output medium

## Procedure

1. Apply the brand-neutral palette and form heuristics before writing chart code.
2. Validate colors with the runnable OKLab color-difference palette validator.

## Output

A chart/dashboard consistent in light and dark, with accessible colors.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
