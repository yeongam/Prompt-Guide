# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: too many permission dialogs, reduce prompts

## Procedure

1. Read recent transcript for repeated tool calls.
2. Extract safe read-only patterns.
3. Add allowlist entries to settings.json.

## Output

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
