# Session Start Hook

- Slug: `session-start-hook`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/session-start-hook`
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Output

Creates a SessionStart hook ensuring the project can run tests and linters.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.
