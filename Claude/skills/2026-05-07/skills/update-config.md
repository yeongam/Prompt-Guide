# Update Config (Settings)

- Slug   : `update-config`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: automated behavior requests; allow/deny permissions; set env vars

## Procedure

1. Identify target: .claude/settings.json (project) or ~/.claude/settings.json (user).
2. Write hooks, permissions, or env entries.
3. Validate JSON before saving.

## Output

Updated settings.json with requested configuration.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
