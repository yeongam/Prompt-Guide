# undo

- Slug: `undo`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to undo last action

## Procedure

Command: `/undo`

Alias for /rewind; undoes last assistant action

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.