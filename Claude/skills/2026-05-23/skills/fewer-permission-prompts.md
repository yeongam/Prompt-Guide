# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants fewer permission dialogs during sessions

## Procedure

1. Scan recent transcripts for repeated Bash/MCP tool calls.
2. Identify patterns that are always read-only or safe.
3. Add allowlist entries to .claude/settings.json.

## Output

Updated allowlist in .claude/settings.json.

## Token Policy

- List only newly added allowlist entries.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.