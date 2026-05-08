# Fewer Permission Prompts

- Slug: `fewer-permission-prompts`
- Command: `/fewer-permission-prompts`
- Trigger: user wants fewer permission dialogs during sessions
- Source: https://github.com/anthropics/claude-code

## Description

Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## Procedure

1. Read recent transcripts for repeated tool calls.
2. Identify safe read-only bash and MCP patterns.
3. Add to allowList in .claude/settings.json.
4. Confirm with user before writing.

## Output

Updated allowList in settings.json.

## Token Policy

- List only new entries being added.
