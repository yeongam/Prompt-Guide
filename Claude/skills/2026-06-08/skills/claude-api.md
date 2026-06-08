# claude-api

- Slug: `claude-api`
- Source: https://github.com/anthropics/claude-code
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Procedure

Command: `/claude-api`

Build/debug Claude API apps; prompt caching, tool use, model migration

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.