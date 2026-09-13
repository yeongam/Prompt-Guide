# claude-api

- Command: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Output

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
