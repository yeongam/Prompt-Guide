# Usage

- Slug: `usage`
- Cmd: `/usage`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: token usage, cost statistics, spending

## Procedure

1. Aggregate session token counts.
2. Calculate cost at current model rates.
3. Display breakdown by turn.

## Output

Show token usage and cost stats (merged /cost + /stats)

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
