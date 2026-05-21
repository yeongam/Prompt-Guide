# fewer-permission-prompts

- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts -> add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
