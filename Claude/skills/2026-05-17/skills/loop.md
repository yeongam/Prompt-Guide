# Loop

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants recurring task (e.g. 'check every 5m', 'keep running X')
- Note: Example: /loop 5m /review

## Procedure

1. Parse interval (default 10m) and target command.
2. Run command, report status, then sleep.
3. Stop on user request or terminal error.

## Output

Recurring task running at specified interval

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
