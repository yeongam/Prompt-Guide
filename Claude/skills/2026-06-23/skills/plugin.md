---
name: plugin
cmd: /plugin [list|browse|enable|disable|init] [--enabled|--disabled]
trigger: user wants to manage, install, or scaffold Claude Code plugins
added: v2.1.157
---
Manages plugins (skills, hooks, MCP servers, agents bundled together).
- `/plugin list --enabled` / `--disabled`: filter view
- `/plugin browse`: marketplace with projected context cost
- `claude plugin init <name>`: scaffold new plugin locally
- `defaultEnabled: false` in plugin.json: plugins off by default until enabled
