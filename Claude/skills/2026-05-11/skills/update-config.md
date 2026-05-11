# update-config

- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Description

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
