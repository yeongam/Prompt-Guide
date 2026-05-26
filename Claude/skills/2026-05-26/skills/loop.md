# Loop

- Slug: `loop`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user wants recurring task (e.g. 'check every 5m', 'keep running X')

## Procedure

1. Parse interval and target command.
2. Schedule via Monitor or background Bash.
3. Report each iteration result.
4. Stop on user request or error threshold.

## Output

Recurring task status updates.

## Token Policy

- Summarize each run in one line.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
