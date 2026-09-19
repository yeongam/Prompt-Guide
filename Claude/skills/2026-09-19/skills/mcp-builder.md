# MCP Builder

- Slug: `mcp-builder`
- Cmd: (skill, no dedicated slash command)
- Source: https://github.com/anthropics/claude-code (bundled skill, v2.1.278)
- Trigger: user is building an MCP server to integrate an external API (Python FastMCP or Node/TypeScript SDK).

## Procedure

1. Design well-scoped tools rather than a thin API wrapper.
2. Prefer FastMCP (Python) or the official MCP SDK (Node/TS).
3. Validate inputs at the tool boundary.

## Token Policy

- Reference guide only.

## Compatibility

- Do not modify GPT or Gemini directories.
- New entry; no conflict with existing catalog slugs.
