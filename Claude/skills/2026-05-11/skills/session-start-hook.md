# session-start-hook

- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Description

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
