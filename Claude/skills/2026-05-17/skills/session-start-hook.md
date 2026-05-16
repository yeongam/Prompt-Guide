# Session Start Hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants test/lint runners on session start (web Claude Code)

## Procedure

1. Identify test and lint commands from project config.
2. Write SessionStart hook that runs them on startup.
3. Ensure hook exits non-zero on failure to block bad sessions.

## Output

SessionStart hook in .claude/settings.json

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
