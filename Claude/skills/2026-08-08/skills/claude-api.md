# Claude API

- Slug: `claude-api`
- Source: anthropics/claude-code CHANGELOG.md (verified fetch, version 2.1.226)
- Trigger: Code imports the Anthropic SDK, or user asks about Claude API features (pricing, caching, tool use, model choice).

## Procedure

1. Default to Claude Opus 5 (changed this delta; migration path from Opus 4.8 documented).
2. Use `prompt-audit` subcommand (new this delta) to audit prompts/tool descriptions for patterns written for older models.
3. Cover prompt caching, tool use, streaming, and model migration as needed.

## Output

Working Claude API code/config, or a migration/audit report.

## Token Policy

- Reference model IDs from this catalog's `models:` block instead of restating them per answer.
- Link to API docs instead of copying long reference tables.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
