# color

- Slug: `color`
- Command: `/color`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a session color

## Description

Set random session color (no args = random pick)

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
