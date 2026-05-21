# update-config

- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Description

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Emit minimal JSON diff; skip unchanged sections.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
