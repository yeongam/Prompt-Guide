# MCP Builder

- Slug: `mcp-builder`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: User is building an MCP (Model Context Protocol) server to integrate an external API or service.

## Procedure

1. Design well-scoped tools for the target external service (Python/FastMCP or Node/TypeScript SDK).
2. Follow current MCP client behavior: elicitation forms, OAuth redirect handling, header-minting helpers.
3. Verify against a real client connection before calling the server done.

## Output

A working MCP server exposing well-designed tools for the target service.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml` instead of duplicating it here.

## Compatibility

- Do not overwrite existing dated skill snapshots; integrate only if content changed.
- Be aware MCP OAuth, elicitation-form rendering, and header-minting behavior changed across v2.1.229–v2.1.239 — verify against the live client, not memorized behavior.

## Source Summary

Official Claude Code skill/guide for building MCP servers. Related MCP client fixes in this window: OAuth redirect-URI/`127.0.0.1` handling (v2.1.229, v2.1.231), elicitation forms clipped in fullscreen fixed (v2.1.239), `headersHelper` requiring folder trust (v2.1.232).
