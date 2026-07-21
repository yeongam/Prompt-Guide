# Dataviz

- Slug: `dataviz`
- Command: `/dataviz`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user is about to create any chart, graph, plot, or dashboard

## Procedure

1. Pick a chart form matching the data shape.
2. Apply the validated default palette (perceptual OKLab-checked).
3. Style for both light and dark themes.

## Output

Chart/dashboard code following the bundled color and layout guidance.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Bundled skill for chart/dashboard design guidance with a runnable color-palette validator; palette and color-blindness thresholds are recalibrated in current releases.
