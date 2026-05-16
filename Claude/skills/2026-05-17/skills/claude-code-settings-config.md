# Claude Code Settings Config

- Slug: `claude-code-settings-config`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User edits .claude/settings.json or ~/.claude/settings.json

## Procedure

1. Project: .claude/settings.json; user: ~/.claude/settings.json.
2. Permissions: allowedTools/deniedTools arrays.
3. Hooks: hooks object keyed by lifecycle event.
4. Env vars: env object with string key-value pairs.
5. Validate JSON before saving.

## Output

Valid settings.json with requested configuration

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
