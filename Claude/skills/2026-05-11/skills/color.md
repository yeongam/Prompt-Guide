# color

- Cmd: `/color`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a session color

## Description

Set random session color (no args = random pick)

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
