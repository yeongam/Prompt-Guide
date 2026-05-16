# Claude API

- Slug: `claude-api`
- Command: `/claude-api`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: Code imports anthropic SDK; user asks about Claude API features

## Procedure

1. Use model IDs: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001.
2. Add prompt caching on system/large context blocks.
3. Implement tool use with minimal JSON schema.
4. Handle streaming where latency matters.
5. Migrate deprecated model references.

## Output

Optimized Claude API code with prompt caching

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
