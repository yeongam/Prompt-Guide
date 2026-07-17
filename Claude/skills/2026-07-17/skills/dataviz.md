# Dataviz

- Slug: `dataviz`
- Command: auto-triggered skill (no slash command)
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212` (added `2.1.163`-ish window; first seen this sync)
- Trigger: about to create any chart, graph, plot, dashboard, or data visualization in any medium

## Summary

Chart and dashboard design guidance, including a runnable color-palette
validator, so generated visualizations read as one consistent, accessible
system (light/dark aware) instead of ad hoc chart-library defaults.

## Token Policy

- Load once before the first chart-code line; reuse the same palette/spec choices across a session instead of re-deriving per chart.

## Compatibility

- Additive; does not conflict with `artifact-design` (page-level) — this is chart/mark-level.
