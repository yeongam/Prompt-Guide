# loop

- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants recurring task (e.g. "check every 5m", "keep running X")

## Description

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
