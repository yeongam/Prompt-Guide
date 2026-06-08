# usage

- Slug: `usage`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks about token or cost statistics

## Procedure

Command: `/usage`

Show token usage and cost stats (merged /cost + /stats)

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.