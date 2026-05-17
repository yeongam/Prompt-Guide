# review

- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
