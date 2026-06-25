# session-start-hook

**cmd:** `/session-start-hook`
**trigger:** user wants test/lint runners on session start (web Claude Code)
**desc:** Create SessionStart hook ensuring project can run tests and linters

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.