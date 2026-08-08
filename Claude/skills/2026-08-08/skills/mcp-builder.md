# MCP Builder

- Slug: `mcp-builder`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: User is building an MCP server to wrap an external API/service as LLM tools.

## Procedure

1. Prefer FastMCP for Python, the official MCP SDK for Node/TypeScript.
2. Design tool schemas around what an LLM caller actually needs, not a 1:1 API mirror.
3. Validate against the target client (Claude Code, Claude Desktop, etc.).

## Output

A working MCP server exposing well-designed tools for the target API.

## Token Policy

- Keep tool descriptions short and decision-relevant.
- Avoid restating the wrapped API's full reference docs in tool descriptions.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
