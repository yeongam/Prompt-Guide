# Usage

- Slug: `usage`
- Command: `/usage`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User asks about token or cost statistics

## Procedure

1. Collect token usage from current session.
2. Calculate cost by model tier.
3. Display summary with per-turn breakdown.

## Output

Token usage and cost breakdown

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
