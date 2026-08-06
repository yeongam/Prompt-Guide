# Claude API

- Slug: `claude-api`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/claude-api`
- Trigger: code imports the Anthropic SDK; user asks about Claude API features

## Output

Build/debug Claude API apps; prompt caching, tool use, model migration.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.
