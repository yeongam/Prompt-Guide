# MCP Builder

- Slug: `mcp-builder`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user is building an MCP server to integrate an external API or service

## Procedure

1. Design well-scoped tools around the target external service.
2. Implement with FastMCP (Python) or the MCP SDK (Node/TypeScript).

## Output

A working MCP server exposing well-designed tools to LLM clients.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
