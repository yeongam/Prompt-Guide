# Claude API

- Slug: `claude-api`
- Command: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: code imports anthropic SDK; user asks about Claude API

## Description

Build/debug/migrate Claude API apps; caching, tools, model IDs

## Procedure

1. Check import: anthropic / @anthropic-ai/sdk.
2. Apply prompt caching by default.
3. Use current models: opus-4-8, sonnet-4-6, haiku-4-5.
4. Validate tool schemas strictly.

## Output

Working code with caching; migration notes if applicable.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Models

- opus: `claude-opus-4-8`
- sonnet: `claude-sonnet-4-6`
- haiku: `claude-haiku-4-5-20251001`
