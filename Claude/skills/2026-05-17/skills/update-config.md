# Update Config

- Slug: `update-config`
- Command: `/update-config`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: Automated behavior requests: 'when X', 'allow Y', 'set Z=val'

## Procedure

1. Determine if change is project-level or user-level.
2. Edit the correct settings.json file.
3. Use hooks for automated behaviors, permissions for tool access.
4. Validate JSON after editing.

## Output

Updated .claude/settings.json or ~/.claude/settings.json

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
