# Update Config

- Slug: `update-config`
- Command: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: automated behavior: 'when X', 'allow Y', 'set Z=val'

## Description

Configure settings.json: hooks, permissions, env vars

## Procedure

1. Parse intent: hook/permission/env var.
2. Read existing .claude/settings.json.
3. Apply minimal targeted edit.

## Output

Patched settings.json with change summary.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
