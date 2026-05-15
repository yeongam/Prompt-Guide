# color

- Cmd: `/color`
- Trigger: user wants a session color
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Set random session color (no args = random pick)

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
