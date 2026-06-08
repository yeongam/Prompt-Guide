# powerup

- Slug: `powerup`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants feature demos or to learn Claude Code features

## Procedure

Command: `/powerup`

Interactive animated feature demos with lessons

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.