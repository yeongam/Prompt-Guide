# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants fewer permission dialogs during Claude Code sessions

## Procedure

1. Scan recent transcripts for repeated read-only Bash and MCP tool calls.
2. Rank by frequency.
3. Build prioritized allowlist.
4. Add to `.claude/settings.json` → `allowedTools`.

## Output

Updated `.claude/settings.json` with allowlist entries; count of entries added.

## Token Policy

- Return allowlist JSON only.
- Prioritize top-10 most frequent.
- No verbose explanation per entry.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
