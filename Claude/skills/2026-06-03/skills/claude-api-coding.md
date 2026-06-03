# Claude API Coding

- Slug: `claude-api-coding`
- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Source branch: `main`
- Catalog version: `2.1.161`
- Trigger: code imports anthropic SDK; user asks about Claude API features, prompt caching, tool use, model migration

## Procedure

1. Check official Anthropic SDK alignment first.
2. Default to latest capable model.
3. Include prompt caching on all builds.
4. Prefer smallest working implementation.
5. Verify with narrowest relevant command.

## Output

Compact Claude API / Anthropic SDK implementation with caching applied.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
