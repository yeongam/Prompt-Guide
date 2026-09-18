# Run

- Slug: `run`
- Command: `/run`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Launch and drive the project's app to verify a change works live.

## Procedure

1. Prefer an existing project skill for launching the app.
2. Otherwise fall back to a built-in pattern for the project type.
3. Exercise the golden path and edge cases before reporting success.

## Output

A running app session confirming the change, or a screenshot.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
