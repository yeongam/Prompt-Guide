# Loop Task

- Slug: `loop`
- Cmd: `/loop [interval] [/command]`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants recurring task (e.g. check every 5m, keep running X)

## Procedure

1. Parse interval (default 10m).
2. Register loop.
3. Execute command on each tick.
4. Stop on /stop or user request.

## Output

Recurring task registered with interval.

## Token Policy

- Log tick count, not full output each time.
- Summarize across ticks on stop.

## Example

`/loop 5m /review`

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
