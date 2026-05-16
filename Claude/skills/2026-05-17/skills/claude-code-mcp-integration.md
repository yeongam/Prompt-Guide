# Claude Code MCP Integration

- Slug: `claude-code-mcp-integration`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User sets up or debugs MCP servers in Claude Code

## Procedure

1. Add server to mcpServers section of settings.json.
2. Specify command, args, env for server process.
3. Use type: stdio for local process servers.
4. Test with /mcp to verify connection.
5. Grant permissions via allowedTools for auto-approval.

## Output

Working MCP server in .claude/settings.json

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
