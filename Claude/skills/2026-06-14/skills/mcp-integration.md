# MCP Server Integration

- Slug: `mcp-integration`
- Source: https://github.com/anthropics/model-context-protocol
- Source commit: `bootstrap-2026-06-13`
- Trigger: Use when building or connecting MCP servers, tools, or resources to Claude.

## Procedure

1. Check official Anthropic source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Concise MCP server setup and tool-definition checklist.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Model Context Protocol — standard for tool/server integrations with Claude.
