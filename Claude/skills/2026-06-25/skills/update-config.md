# update-config

**cmd:** `/update-config`
**trigger:** automated behavior requests ("when X", "allow Y", "set Z=val")
**desc:** Configure settings.json; handles hooks, permissions, env vars

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.