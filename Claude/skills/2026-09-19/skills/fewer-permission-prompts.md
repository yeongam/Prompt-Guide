# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Scan transcripts for common read-only calls, allowlist them.

## Procedure

1. Scan recent transcripts for repeated safe Bash/MCP calls.
2. Add a prioritized allowlist to project .claude/settings.json.
3. Never allowlist destructive or write-scope commands.

## Output

Expanded settings.json permissions allowlist.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
