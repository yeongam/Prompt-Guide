# Usage

- Slug: `usage`
- Command: `/usage`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks about token or cost statistics

## Description

Show token usage and cost stats (merged /cost + /stats)

## Procedure

1. Aggregate session token counts.
2. Show cost breakdown.

## Output

Token usage and cost report.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
