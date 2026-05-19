# fewer-permission-prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
