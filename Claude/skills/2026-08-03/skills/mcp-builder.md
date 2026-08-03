# MCP Server Builder

- Slug: `mcp-builder`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Building an MCP server (Python FastMCP or Node/TypeScript SDK) to expose an external API/service as tools.

## Procedure

1. Confirm target runtime (Python FastMCP vs Node/TypeScript MCP SDK).
2. Design tool boundaries around discrete external-API operations, not raw endpoint pass-through.
3. Validate inputs/outputs against the service's actual schema.
4. Keep tool descriptions short and action-oriented for model callability.
5. Smoke-test each tool against a live or sandboxed instance of the service.

## Output

High-quality MCP server scaffold with well-designed, LLM-callable tools.

## Token Policy

- Reference the skill's bundled guide instead of re-deriving MCP conventions.
- Avoid duplicating SDK boilerplate already covered by the skill's templates.

## Compatibility

- Additive only; does not alter existing Claude/skills catalog entries.
- No slug collision with prior catalog (`init`, `review`, `security-review`, etc.).
