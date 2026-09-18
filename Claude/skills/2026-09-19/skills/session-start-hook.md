# Session Start Hook

- Slug: `session-start-hook`
- Command: `/session-start-hook`
- Category: docs
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Create a SessionStart hook so web sessions can run tests/linters.

## Procedure

1. Detect the project's test and lint commands.
2. Write a SessionStart hook entry in settings.json.
3. Verify the hook runs cleanly on a fresh session.

## Output

SessionStart hook wired into .claude/settings.json.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
