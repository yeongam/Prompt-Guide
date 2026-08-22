# Claude API Programming

- Slug: `claude-api`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: Code imports the Anthropic SDK, or user asks about Claude API usage.

## Procedure

1. Confirm current model IDs and SDK version in use.
2. Apply prompt caching and tool-use patterns correctly.
3. Flag deprecated SDK 0.x patterns when migrating to 1.x.
4. Verify with the narrowest relevant request or test.

## Output

Working Claude API integration with current SDK conventions.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
