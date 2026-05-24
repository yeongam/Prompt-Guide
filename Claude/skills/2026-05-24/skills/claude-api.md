# Claude API

- Slug: `claude-api`
- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: code imports anthropic SDK, Claude API features, model migration

## Procedure

1. Identify SDK version and feature area.
2. Apply prompt caching and tool use best practices.
3. Migrate model IDs to latest versions.

## Output

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
