# theme

- Slug: `theme`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to change or create visual theme

## Procedure

Command: `/theme [name]`

Create or switch custom color themes

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.