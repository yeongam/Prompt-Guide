# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants fewer permission dialogs

## Procedure

1. Scan transcripts for repeated bash and MCP tool calls.
2. Identify safe, read-only patterns to allowlist.
3. Add allowlist entries to .claude/settings.json.
4. Prioritize by frequency of prompting.

## Output

Allowlist added to .claude/settings.json

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
