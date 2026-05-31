# session-start-hook

- Slug: `session-start-hook`
- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants test/lint runners on session start (web Claude Code).

## Procedure

1. Detect project type and test/lint commands.
2. Create SessionStart hook in .claude/settings.json.
3. Verify hook fires on next session start.

## Output

SessionStart hook configured.

## Token Policy

- Single settings.json write; no repeated reads.

## Compatibility

- Web Claude Code sessions only.
