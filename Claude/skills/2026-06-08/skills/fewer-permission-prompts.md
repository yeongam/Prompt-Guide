# fewer-permission-prompts

- Slug: `fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants fewer permission dialogs

## Procedure

Command: `/fewer-permission-prompts`

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.