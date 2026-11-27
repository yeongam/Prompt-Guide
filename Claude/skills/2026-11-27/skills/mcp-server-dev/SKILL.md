---
name: mcp-server-dev
description: Design, build, bundle, or integrate an MCP server/app. Use on "build an MCP server", "MCP app/widget", "package .mcpb", "add .mcp.json".
---
# MCP Server Dev
Src: claude-plugins-official/{mcp-server-dev,plugin-dev/mcp-integration}@0fbfda5a91f4
1. Interrogate: upstream system, users, # actions, need for UI/elicitation, auth.
2. Deploy model: remote streamable-HTTP (default) | MCP app (HTTP+UI) | MCPB (local, bundled runtime) | stdio (dev only).
3. Tool pattern: ≤~15 actions → one tool per action; larger → search + execute.
4. Framework: TS MCP SDK or Python FastMCP; scaffold, then add resources/prompts only if needed.
5. Integrate: `.mcp.json` / plugin `mcpServers`, `${CLAUDE_PLUGIN_ROOT}` paths, env for secrets.
6. Test in Claude (`/mcp`), then publish.
