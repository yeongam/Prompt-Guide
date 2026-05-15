# session-start-hook

- Cmd: `/session-start-hook`
- Trigger: user wants test/lint runners on session start (web Claude Code)
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
