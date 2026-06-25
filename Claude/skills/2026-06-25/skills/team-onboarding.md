# team-onboarding

**cmd:** `/team-onboarding`
**trigger:** user wants teammate ramp-up guide
**desc:** Generate onboarding guide from local Claude Code usage history/data

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.