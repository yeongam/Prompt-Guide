# update-config

- Command: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Output

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
