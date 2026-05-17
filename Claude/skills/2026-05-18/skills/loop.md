# loop

- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants recurring task (e.g. "check every 5m", "keep running X")

## Description

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
