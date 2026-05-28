# MCP Integration

- Slug: `mcp-integration`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use for adding MCP servers, defining tools, and connecting external resources.

## Procedure

1. Choose transport: stdio (local) or SSE/HTTP (remote).
2. Define tool name, description, and input_schema precisely.
3. Add server config under mcpServers in settings.json.
4. Verify tool appears via /mcp before testing.
5. Keep tool descriptions short — they consume context on every call.

## Output

Minimal MCP server config ready for claude_desktop_config.json or settings.json.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude Code ![](https://img.shields.io/badge/Node.js-18%2B-brightgreen?style=flat-
square) [![npm]](https://www.npmjs.com/package/@anthropic-ai/claude-code) [npm]:
https://img.shields.io/npm/v/@anthropic-ai/claude-code.svg?style=flat-square Claude Code
is an agentic coding tool that lives in your terminal, understands your codebase, and
helps you code faster by executing routine tasks, explaining complex code, and.
