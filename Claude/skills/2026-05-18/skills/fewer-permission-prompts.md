# fewer-permission-prompts

- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
