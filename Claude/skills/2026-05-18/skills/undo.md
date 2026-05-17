# undo

- Cmd: `/undo`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants to undo last action

## Description

Alias for /rewind; undoes last assistant action

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
