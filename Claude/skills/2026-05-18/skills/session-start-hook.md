# session-start-hook

- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Description

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
