# Session Start Hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Trigger: user wants test/lint runners to fire on session start
- Source: https://github.com/anthropics/claude-code

## Description

Create SessionStart hook ensuring project can run tests and linters

## Procedure

1. Detect test runner (pytest, jest, go test, etc.).
2. Detect linter (eslint, ruff, golangci-lint, etc.).
3. Write SessionStart hook in .claude/settings.json.
4. Verify hook fires on next session start.

## Output

SessionStart hook entry in settings.json.

## Token Policy

- Show only the hook config block, not full settings.
