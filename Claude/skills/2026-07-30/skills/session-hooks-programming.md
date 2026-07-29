# Session Hooks Programming

- Slug: `session-hooks-programming`
- Command: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User wants test/lint runners on session start (web Claude Code).

## Procedure

1. Create a SessionStart hook in .claude/settings.json.
2. Verify the hook runs project test/lint commands.

## Output

SessionStart hook wired to project test/lint commands.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.
