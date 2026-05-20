# Claude API

- Slug: `claude-api`
- Cmd: `/claude-api`
- Source: anthropics/claude-code v2.1.145
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Procedure

1. Identify SDK usage pattern.
2. Apply prompt caching where applicable.
3. Use correct model ID.
4. Verify tool use schema.

## Output

Working API code with caching and correct model IDs.

## Token Policy

- Show only changed code blocks.
- Reference SDK docs by URL, not inline copy.

## Models

- opus: `claude-opus-4-7`
- sonnet: `claude-sonnet-4-6`
- haiku: `claude-haiku-4-5-20251001`

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
