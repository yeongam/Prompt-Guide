# Color

- Slug: `color`
- Command: `/color`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a session color

## Description

Set random session color

## Procedure

1. Pick random color if no args.
2. Apply to session.

## Output

Session color set.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
