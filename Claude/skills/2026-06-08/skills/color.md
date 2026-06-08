# color

- Slug: `color`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a session color

## Procedure

Command: `/color`

Set random session color (no args = random pick)

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.