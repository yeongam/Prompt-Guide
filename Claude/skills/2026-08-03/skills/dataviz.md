# Data Visualization

- Slug: `dataviz`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Before writing any chart/graph/plot/dashboard code, in any medium (HTML/React artifact, SVG, matplotlib/plotly/d3/Recharts, Slack image).

## Procedure

1. Read before writing the first line of chart code, picking colors, or laying out a dashboard.
2. Apply the form heuristic and color formula (validated default palette in `references/palette.md`) rather than ad hoc choices.
3. Style consistently in both light and dark themes.

## Output

Charts/dashboards that read as one consistent, accessible visual system.

## Token Policy

- Reference the palette/validator file instead of re-deriving color math per chart.

## Compatibility

- Additive only; no collision with existing catalog entries.
