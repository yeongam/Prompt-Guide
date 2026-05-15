# loop

- Cmd: `/loop [interval] [/command]`
- Trigger: user wants recurring task (e.g. 'check every 5m', 'keep running X')
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
