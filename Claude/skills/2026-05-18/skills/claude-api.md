# claude-api

- Cmd: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Description

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
