# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Cmd: `/fewer-permission-prompts`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants fewer permission dialogs

## Procedure

1. Scan recent transcripts for denied commands.
2. Group by tool type.
3. Add to allowlist.
4. Verify no over-permissioning.

## Output

Updated allowlist in .claude/settings.json.

## Token Policy

- List allowed patterns only.
- Group by tool category.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
