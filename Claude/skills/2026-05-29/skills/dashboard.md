# Dashboard

- Slug: `dashboard`
- Command: `/dashboard`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a dashboard, monitoring view, or metrics page

## Description

Discover data, design panels, implement, validate, open PR

## Procedure

1. Find data sources and existing dashboard patterns.
2. Spec panels and layout.
3. Implement; validate queries and rendering.
4. Open PR.

## Output

Dashboard implementation + PR.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
