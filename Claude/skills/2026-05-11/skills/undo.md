# undo

- Cmd: `/undo`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to undo last action

## Description

Alias for /rewind; undoes last assistant action

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
