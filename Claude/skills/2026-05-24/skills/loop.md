# Loop

- Slug: `loop`
- Cmd: `/loop [interval] [/cmd]`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: recurring task, polling interval, repeated check

## Procedure

1. Parse interval and command.
2. Schedule using internal timer.
3. Execute command on each tick; stop on user request.

## Output

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Example

`/loop 5m /review`
