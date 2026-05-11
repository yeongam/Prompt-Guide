# fewer-permission-prompts

- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
