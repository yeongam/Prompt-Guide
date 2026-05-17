# update-config

- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Description

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
