---
name: plugin-dev
description: Build Claude Code plugins: structure, commands, agents, skills, hooks, MCP, settings.
---
Layout: `.claude-plugin/plugin.json` (required, only here); `commands/ agents/ skills/<n>/SKILL.md hooks/hooks.json .mcp.json scripts/` at root. kebab-case names; only create used dirs; portable paths via `${CLAUDE_PLUGIN_ROOT}`.
Command (.md): frontmatter `description` (<60ch), `allowed-tools` (e.g. `Bash(git:*)`), `model`, `argument-hint`; `$ARGUMENTS`, `@file`, `` !`cmd` ``.
Agent (.md): `name` (3-50, lowercase-hyphen), `description` (when + examples), `model` (default `inherit`), `color`, `tools` (least privilege); body = system prompt.
Skill: `SKILL.md` frontmatter `name`, `description` (third-person triggers); lean body, details in `references/`.
Hooks: events PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification; types command/prompt; matchers per tool; output JSON `decision/reason`, exit 2 blocks. Validate input, quote vars, set timeouts.
MCP: `.mcp.json`; types stdio/SSE/HTTP/WebSocket; env expansion; tools named `mcp__<server>__<tool>`.
Settings: `.claude/<plugin>.local.md` YAML frontmatter + body; gitignore it.
