# Claude API

- Slug: `claude-api`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: code imports the Anthropic SDK or user asks about Claude API features/pricing/limits

## Procedure

1. Confirm current model IDs, pricing, and parameter support.
2. Cover streaming, tool use, MCP, prompt caching, and token counting as needed.
3. For version migrations, use the built-in upgrade path (e.g. anthropic 0.x -> 1.x).

## Output

Correct, current-version Claude API / Anthropic SDK usage or migration.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
