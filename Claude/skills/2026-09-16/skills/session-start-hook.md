# Session Start Hook

- Slug: `session-start-hook`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user wants test/lint runners available in web Claude Code sessions

## Procedure

1. Create a SessionStart hook so the project can run tests and linters.

## Output

Configured SessionStart hook in the repo.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
