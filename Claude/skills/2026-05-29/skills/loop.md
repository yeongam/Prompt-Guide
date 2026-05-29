# Loop

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants recurring task (e.g. 'check every 5m')

## Description

Run prompt or slash command on recurring interval (default 10m)

## Procedure

1. Parse interval and command.
2. Schedule via Monitor tool.
3. Execute on each tick; stop on user request.

## Output

Recurring execution confirmation.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
