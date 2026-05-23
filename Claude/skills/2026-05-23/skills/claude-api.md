# Claude API Development

- Slug: `claude-api`
- Command: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: Code imports anthropic SDK; user asks about Claude API features or model migration

## Procedure

1. Identify SDK version and current model IDs in use.
2. Apply prompt caching where repeated context exists.
3. Validate tool_use schema against latest spec.
4. Check model IDs: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001.
5. For migrations: replace retired model IDs, update deprecated params.

## Output

Updated SDK code with caching, correct model IDs, validated tool schemas.

## Token Policy

- Show only changed code blocks, not full file reprints.
- Reference API docs URL instead of reproducing parameter lists.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.