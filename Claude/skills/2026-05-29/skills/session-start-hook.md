# Session Start Hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants test/lint runners on session start

## Description

Create SessionStart hook in .claude/settings.json

## Procedure

1. Detect test/lint commands from project files.
2. Write SessionStart hook to .claude/settings.json.

## Output

Updated .claude/settings.json with SessionStart hook.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
