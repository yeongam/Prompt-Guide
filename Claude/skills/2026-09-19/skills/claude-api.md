# Claude API

- Slug: `claude-api`
- Command: `/claude-api`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Reference for the Claude API / Agent SDK: models, tools, caching.

## Procedure

1. Identify the current model ids and pricing before quoting old ones.
2. Prefer prompt caching and streaming where applicable.
3. Cross-check tool-use and MCP integration patterns.

## Output

Correct, current guidance for Claude API/SDK usage.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
