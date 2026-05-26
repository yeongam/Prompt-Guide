# Session Start Hook

- Slug: `session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Procedure

1. Detect test runner (pytest, jest, vitest, etc.).
2. Detect linter (eslint, ruff, mypy, etc.).
3. Write SessionStart hook to .claude/settings.json.
4. Verify hook syntax and permissions.

## Output

SessionStart hook entry in settings.json.

## Token Policy

- Return only the JSON hook config block.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
