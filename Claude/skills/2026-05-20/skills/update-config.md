# update-config

- Slug: `update-config`
- Command: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Description

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
