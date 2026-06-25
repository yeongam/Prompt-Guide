# effort

**cmd:** `/effort`
**trigger:** user wants to adjust effort/quality level
**desc:** Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.