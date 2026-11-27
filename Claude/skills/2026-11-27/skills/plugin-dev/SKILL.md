---
name: plugin-dev
description: Build Claude Code plugins, skills, slash commands, subagents, hooks, hookify rules, or plugin settings. Use on "create a plugin/skill/command/agent/hook".
---
# Plugin Dev
Src: claude-plugins-official/{plugin-dev,skill-creator,hookify}@0fbfda5a91f4
Layout: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/<name>/SKILL.md`, `hooks/hooks.json`, `.mcp.json`; reference files via `${CLAUDE_PLUGIN_ROOT}`.
- skill: frontmatter `name`+`description` (trigger phrases); body lean; move detail to referenced files (progressive disclosure). Check cost with `/skill-doctor`; reload with `/reload-skills`.
- command: frontmatter `description`, `argument-hint`, `allowed-tools`; `$ARGUMENTS`, `!`cmd`` context, `@file` refs.
- agent: `name`, `description` with when-to-use examples, `tools`, `model`; focused system prompt.
- hook: events PreToolUse/PostToolUse/Stop/SessionStart/UserPromptSubmit/PreCompact/PreSkillShellCommand…; block = exit 2 or `{decision:"block"}`; types shell|mcp_tool|http|prompt.
- hookify: `.claude/hookify.*.local.md` rule = event + pattern + action(warn|block).
- settings: per-project `.claude/<plugin>.local.md` with YAML frontmatter.
Validate: `claude plugin validate <dir>`; test: `claude --plugin-dir <dir>`.
