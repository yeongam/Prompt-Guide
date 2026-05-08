# Update Config

- Slug: `update-config`
- Command: `/update-config`
- Trigger: automated behaviors, permissions, env vars, or settings.json changes
- Source: https://github.com/anthropics/claude-code

## Description

Configure settings.json; hooks, permissions, env vars

## Procedure

1. Identify target: project .claude/settings.json or user ~/.claude/settings.json.
2. For hooks: add shell command or mcp_tool entry under correct lifecycle event.
3. For permissions: add to allow/deny list.
4. Validate JSON before writing.

## Output

Updated settings.json snippet.

## Token Policy

- Show only changed keys, not full file.
