# claude-api

- Cmd: `/claude-api`
- Trigger: code imports anthropic SDK; user asks about Claude API features
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
