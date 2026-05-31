# claude-api

- Slug: `claude-api`
- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: Code imports anthropic SDK; user asks about Claude API features.

## Procedure

1. Identify SDK usage pattern (streaming, tool use, caching, batch).
2. Apply prompt caching by default on large contexts.
3. Use latest model IDs; handle model migrations.

## Output

Working Claude API code with caching applied.

## Token Policy

- cache_control only on static context blocks ≥ 1024 tokens.

## Compatibility

- opus=claude-opus-4-8, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001
