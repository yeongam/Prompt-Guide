# fewer-permission-prompts

- Cmd: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user wants fewer permission dialogs

## Desc

Scan transcripts, add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
