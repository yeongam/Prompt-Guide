# powerup

**cmd:** `/powerup`
**trigger:** user wants feature demos or to learn Claude Code features
**desc:** Interactive animated feature demos with lessons

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.