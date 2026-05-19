# session-start-hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Description

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
