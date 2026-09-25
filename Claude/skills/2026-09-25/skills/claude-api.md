# claude-api

- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: code imports the Anthropic SDK; user asks about Claude API features

## Desc

Build/debug Claude API apps: prompt caching, tool use, model migration

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Models

- opus: `claude-opus-5-5`
- sonnet: `claude-sonnet-5`
- haiku: `claude-haiku-4-5-20251001`
