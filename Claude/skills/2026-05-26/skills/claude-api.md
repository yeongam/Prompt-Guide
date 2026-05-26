# Claude API

- Slug: `claude-api`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Procedure

1. Check SDK import and version compatibility.
2. Apply prompt caching for repeated context.
3. Use structured tool_use for function calls.
4. Select correct model ID for task.
5. Validate response structure before use.

## Output

Working Claude API implementation with caching.

## Token Policy

- Cache system prompts and long static context.
- Return minimal working example; link to docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
