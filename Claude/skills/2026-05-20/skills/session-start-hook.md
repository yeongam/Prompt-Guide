# Session Start Hook

- Slug: `session-start-hook`
- Cmd: `/session-start-hook`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Procedure

1. Detect project type.
2. Find test and lint commands.
3. Write hook entry to settings.json.
4. Verify hook fires on next session.

## Output

SessionStart hook config in .claude/settings.json.

## Token Policy

- Emit only the JSON diff for settings.json.
- Skip explanation if command is self-evident.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
