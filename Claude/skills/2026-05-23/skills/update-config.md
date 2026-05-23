# Update Config

- Slug: `update-config`
- Command: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: Automated behavior requests, permission changes, env var config, settings.json edits

## Procedure

1. Identify target: project .claude/settings.json or user ~/.claude/settings.json.
2. Determine change type: hook, permission, env var, behavior.
3. Apply minimal diff to settings.json.
4. Validate JSON structure after edit.

## Output

Updated settings.json with requested configuration.

## Token Policy

- Show only the changed JSON keys, not the full file.
- One-line explanation per change.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.