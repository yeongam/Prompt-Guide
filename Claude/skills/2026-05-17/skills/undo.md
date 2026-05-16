# Undo

- Slug: `undo`
- Command: `/undo`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants to undo last action

## Procedure

1. Alias for /rewind.
2. Reverts last assistant action in current session.

## Output

Last assistant action reverted

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
