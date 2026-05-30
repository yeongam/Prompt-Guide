# Session Start Hook

- Slug: `session-start-hook`
- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Procedure

1. Detect project type (package.json, pyproject.toml, Makefile, etc.).
2. Identify test command and lint command.
3. Write SessionStart hook to `.claude/settings.json`.
4. Hook runs both commands and surfaces failures before first turn.

## Output

`.claude/settings.json` patch with SessionStart hook added.

## Token Policy

- Return JSON patch only.
- No verbose hook documentation.
- Link to hook schema docs for reference.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
