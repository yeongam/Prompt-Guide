# Usage Stats

- Slug: `usage`
- Cmd: `/usage`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks about token or cost statistics

## Procedure

1. Aggregate token counts.
2. Calculate cost by model.
3. Show breakdown table.

## Output

Token and cost summary for current session.

## Token Policy

- Table format; no narrative.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
