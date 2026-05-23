# Session Start Hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants test/lint runners to fire on session start (web Claude Code)

## Procedure

1. Detect test and lint commands from package.json / Makefile / pyproject.toml.
2. Create SessionStart hook in .claude/settings.json.
3. Ensure hook is non-blocking (no exit 2).

## Output

SessionStart hook entry in .claude/settings.json.

## Token Policy

- Emit only the hook JSON block.
- Skip setup prose if commands are self-explanatory.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.