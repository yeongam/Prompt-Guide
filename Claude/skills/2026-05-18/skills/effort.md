# effort

- Cmd: `/effort`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants to adjust effort/quality level

## Description

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
