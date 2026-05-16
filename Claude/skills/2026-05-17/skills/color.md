# Color

- Slug: `color`
- Command: `/color`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants a session color

## Procedure

1. Pick random color (no args) or apply specified color.

## Output

Random or selected session color applied

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
