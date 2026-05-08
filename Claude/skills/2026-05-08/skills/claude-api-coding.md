# Claude API Coding

- Slug: `claude-api-coding`
- Command: `/claude-api`
- Trigger: code imports anthropic SDK; user asks about Claude API features
- Source: https://github.com/anthropics/anthropic-sdk-python

## Description

Build/debug/optimize Claude API apps; prompt caching, tool use, model migration

## Procedure

1. Check anthropics/anthropic-sdk-python or anthropic-sdk-typescript alignment.
2. Prefer smallest working implementation with prompt caching enabled.
3. Use structured tool_use over ad hoc text parsing.
4. Keep system prompts short; pass context via user turns.
5. Verify with narrowest relevant test or CLI call.

## Output

Compact implementation with caching, correct model ID, and tool schema.

## Token Policy

- Avoid repeating SDK boilerplate—link to docs instead.
- Return only decision-critical code snippets.
- Use cache_control on large static context blocks.

## Models

- opus: `claude-opus-4-7`
- sonnet: `claude-sonnet-4-6`
- haiku: `claude-haiku-4-5-20251001`
