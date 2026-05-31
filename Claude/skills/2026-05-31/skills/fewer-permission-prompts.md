# fewer-permission-prompts

- Slug: `fewer-permission-prompts`
- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants fewer permission dialogs.

## Procedure

1. Scan transcripts for repeated read-only Bash/MCP calls.
2. Add allowlist entries to .claude/settings.json.
3. Prioritize high-frequency safe commands.

## Output

Updated settings.json with allowlist; count of rules added.

## Token Policy

- Single-pass scan; batch allowlist entries per tool type.

## Compatibility

- No destructive commands added to allowlist.
