# claude-api

- Slug: `claude-api`
- Command: `/claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Description

Build/debug Claude API apps; prompt caching, tool use, model migration

## Notes

- models: 

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
