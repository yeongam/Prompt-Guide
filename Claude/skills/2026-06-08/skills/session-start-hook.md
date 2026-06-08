# session-start-hook

- Slug: `session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Procedure

Command: `/session-start-hook`

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.