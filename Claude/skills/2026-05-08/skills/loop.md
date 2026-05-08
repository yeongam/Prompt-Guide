# Loop (Recurring Task)

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Trigger: user wants recurring task or polling (e.g. 'check every 5m')
- Source: https://github.com/anthropics/claude-code

## Description

Run prompt or slash command on recurring interval (default 10m)

## Procedure

1. Parse interval (e.g. 5m, 1h) and target command.
2. Schedule via Monitor tool; wake on each tick.
3. Execute target; log result.
4. Stop on user cancel or error threshold.

## Output

Recurring execution log; summary on stop.

## Token Policy

- Suppress unchanged results; log diffs only.
