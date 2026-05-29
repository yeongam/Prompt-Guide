# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts; add bash/MCP allowlist to .claude/settings.json

## Procedure

1. Scan recent transcripts for repeated tool calls.
2. Build allowlist of safe patterns.
3. Add to allowedTools in .claude/settings.json.

## Output

Allowlist additions to settings.json.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
