# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.196`
- Source commit: `c80896ca84bd`
- Trigger: user wants fewer permission dialogs

## Description

Scan transcripts -> add bash/MCP allowlist to .claude/settings.json

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Keep prompt and code paths short.
4. Verify with narrowest relevant command.
5. Link to source docs instead of copying long content.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
