# Claude API

- Slug: `claude-api`
- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: code imports `anthropic`/`@anthropic-ai/sdk`; user asks about Claude API features, prompt caching, tool use, model migration

## Procedure

1. Check official source alignment first.
2. Default to latest capable model (`claude-sonnet-4-6` or `claude-opus-4-7`).
3. Include prompt caching on all multi-turn or repeated-context calls.
4. Use structured tool_use over ad hoc parsing.
5. Keep prompt and code paths short.
6. Verify with the narrowest relevant test.

## Models

| Role | ID |
|------|----|
| Opus | claude-opus-4-7 |
| Sonnet | claude-sonnet-4-6 |
| Haiku | claude-haiku-4-5-20251001 |

## Output

Minimal Claude API implementation with caching and tool use wired in.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code.
- Link to Anthropic docs instead of copying long specs.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
