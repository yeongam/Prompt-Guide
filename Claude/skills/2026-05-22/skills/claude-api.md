# claude-api

- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Description

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Enable prompt caching on all multi-turn builds.
- Prefer structured tool_use over free-text parsing.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
