# Session Start Hook

- Slug: `session-start-hook`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: User wants test/lint runners available on web session start.

## Procedure

1. Detect the project's test and lint commands.
2. Create a SessionStart hook that prepares the environment.
3. Keep the hook narrowly scoped to what the project needs.

## Output

SessionStart hook enabling tests/linters in web sessions.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
