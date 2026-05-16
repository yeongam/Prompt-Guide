# Claude Code Hook Authoring

- Slug: `claude-code-hook-authoring`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User writes PreToolUse, PostToolUse, Stop, or lifecycle hooks

## Procedure

1. Choose hook type: shell command, mcp_tool, or http endpoint.
2. Blocking: exit 2 or JSON {decision:'block', reason:'...'}.
3. PreToolUse: read tool_name and tool_input from stdin JSON.
4. PostToolUse: read tool_name, tool_input, tool_output from stdin.
5. Keep hooks fast; slow hooks delay every tool call.

## Output

Shell or MCP hook script integrated with Claude Code lifecycle

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
