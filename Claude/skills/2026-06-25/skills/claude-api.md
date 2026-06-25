# claude-api

**cmd:** `/claude-api`
**trigger:** code imports anthropic SDK; user asks about Claude API features
**desc:** Build/debug Claude API apps; prompt caching, tool use, model migration

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.