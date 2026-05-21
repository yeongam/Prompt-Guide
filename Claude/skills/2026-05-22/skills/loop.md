# loop

- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user wants recurring task (e.g. "check every 5m", "keep running X")

## Description

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

## Example

```
/loop 5m /review
```

