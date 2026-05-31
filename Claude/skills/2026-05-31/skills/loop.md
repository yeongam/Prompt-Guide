# loop

- Slug: `loop`
- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants recurring task, e.g. 'check every 5m'.

## Procedure

1. Parse interval and target command.
2. Schedule via internal timer; default = 10m.
3. Execute target on each tick; report changes only.

## Output

Recurring execution started; summary per tick.

## Token Policy

- Report diffs only; suppress 'no change' ticks.

## Compatibility

- Works with any slash command as target.
