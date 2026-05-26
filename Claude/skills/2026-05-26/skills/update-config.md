# Update Config

- Slug: `update-config`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: automated behavior requests ('when X', 'allow Y', 'set Z=val')

## Procedure

1. Parse user intent: hook vs permission vs env var.
2. Read current .claude/settings.json.
3. Merge new config without breaking existing entries.
4. Write updated file.

## Output

Updated settings.json diff.

## Token Policy

- Return only changed JSON keys.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
