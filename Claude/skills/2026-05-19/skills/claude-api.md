# Claude API

- Slug: `claude-api`
- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Catalog version: `2.1.143`
- Trigger: Code imports anthropic SDK; user asks about Claude API features

## Procedure

1. Confirm trigger matches user intent before invoking.
2. Prefer smallest effective invocation.
3. Keep output scoped to the specific request.
4. Do not add unrequested features or refactors.
5. Verify result without re-reading unchanged files.

## Output

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Avoid repeating background context already in conversation.
- Return only decision-critical output.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

## Notes

- Models: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001
