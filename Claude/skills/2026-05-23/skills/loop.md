# Loop Task

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants recurring task (e.g. 'check every 5m', 'keep running X')

## Procedure

1. Parse interval (default 10m) and command.
2. Schedule recurring execution via Monitor or background Bash.
3. Stop on user request or terminal condition.

## Output

Recurring task runner active at specified interval.

## Token Policy

- Log only delta output per iteration, not full state.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.