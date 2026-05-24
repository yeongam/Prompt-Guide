# Undo

- Slug: `undo`
- Cmd: `/undo`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: undo last action, revert last change

## Procedure

1. Identify last assistant action.
2. Revert file changes or tool effects.
3. Confirm revert to user.

## Output

Alias for /rewind; undoes last assistant action

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
