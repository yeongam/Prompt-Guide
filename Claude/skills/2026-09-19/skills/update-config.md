# Update Config

- Slug: `update-config`
- Command: `/update-config`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Configure the Claude Code harness via settings.json.

## Procedure

1. Resolve target scope: project vs user settings.
2. Edit hooks, permissions, or env vars as requested.
3. Validate JSON before saving.

## Output

Updated settings.json/settings.local.json.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
