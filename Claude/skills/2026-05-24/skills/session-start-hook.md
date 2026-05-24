# Session Start Hook

- Slug: `session-start-hook`
- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: test/lint runners on session start (web Claude Code)

## Procedure

1. Detect test and lint commands from package.json/Makefile.
2. Write hook config to .claude/settings.json.
3. Verify hook fires on next session start.

## Output

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
