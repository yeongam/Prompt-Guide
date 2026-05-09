# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Version: 2.1.138
- Source: https://github.com/anthropics/claude-code  (commit `831608a36051`)
- Trigger: user wants fewer permission dialogs

## Output

Scan transcripts → bash/MCP allowlist in .claude/settings.json

## Procedure

1. Confirm user intent matches skill trigger.
2. Execute skill command with minimal arguments.
3. Return only decision-critical output.
4. Skip background context already visible in session.

## Token Policy

- Return only decision-critical output.
- Omit redundant background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
