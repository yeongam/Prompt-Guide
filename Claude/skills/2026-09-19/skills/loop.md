# Loop

- Slug: `loop`
- Command: `/loop`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Run a prompt or slash command on a recurring interval.

## Procedure

1. Parse the interval, or self-pace when none is given.
2. Re-invoke the same prompt/command each cycle.
3. Stop cleanly via the loop's own stop condition.

## Output

A scheduled recurring task.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
