# fewer-permission-prompts

- Command: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: user wants fewer permission dialogs

## Output

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
