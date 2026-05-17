# usage

- Cmd: `/usage`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user asks about token or cost statistics

## Description

Show token usage and cost stats (merged /cost + /stats)

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
