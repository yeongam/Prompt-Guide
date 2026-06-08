# update-config

- Slug: `update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Procedure

Command: `/update-config`

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.