# Undo

- Slug: `undo`
- Command: `/undo`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to undo last action

## Description

Alias for /rewind; undoes last assistant action

## Procedure

1. Invoke /rewind.
2. Restore previous state.

## Output

Last action undone.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
