# Update Config

- Slug: `update-config`
- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: automated behavior requests, permissions, env vars, settings.json

## Procedure

1. Parse user intent (hook / permission / env var).
2. Locate correct settings.json scope (project vs user).
3. Apply change with minimal diff.

## Output

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
