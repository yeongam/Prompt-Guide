# Undo Action

- Slug: `undo`
- Cmd: `/undo`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants to undo last action

## Procedure

1. Identify last action.
2. Revert it.
3. Confirm state.

## Output

Last action undone.

## Token Policy

- One-line confirmation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
