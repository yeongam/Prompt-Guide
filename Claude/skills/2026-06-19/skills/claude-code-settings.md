# Claude Code Settings
# Source: anthropics/claude-code v2.1.183
# Date: 2026-06-19
# Location: .claude/settings.json (project) | ~/.claude/settings.json (user)

## Display & UX
autoScrollEnabled          bool    — Disable auto-scroll in fullscreen TUI
showThinkingSummaries      bool    — Thinking summary generation (default: false)
wheelScrollAccelerationEnabled bool — Disable mouse-wheel acceleration
language                   string  — Session title generation language (v2.1.176)
footerLinksRegexes         list    — Regex-matched link badges in footer (v2.1.176)
skillOverrides             enum    — off | user-invocable-only | name-only

## Security & Permissions
attribution.sessionUrl     bool    — Omit claude.ai session link from commits/PRs (v2.1.183)
sandbox.allowAppleEvents   bool    — Enable Apple Events on macOS (v2.1.181)
sandbox.network.deniedDomains list — Block specific domains (v2.1.85)
disableSkillShellExecution bool    — Disable inline shell exec in skill definitions
disableBundledSkills       bool    — Hide bundled skills/workflows/commands (v2.1.169)

## Model & Execution
fallbackModel              list    — Up to 3 fallback models in order (v2.1.166)
enforceAvailableModels     bool    — Block widening of managed availableModels (v2.1.175)
availableModels            list    — Restrict selectable models
prUrlTemplate              string  — Custom URL template for PR footer badge

## Agent & Worktree
worktree.bgIsolation       enum    — "none" allows direct edits in bg worktrees (v2.1.143)
worktree.baseRef           string  — Base ref for worktree (e.g. "head")

## Managed / Enterprise
requiredMinimumVersion     string  — Enforce minimum Claude Code version (v2.1.163)
requiredMaximumVersion     string  — Enforce maximum Claude Code version (v2.1.163)
allowAllClaudeAiMcps       bool    — Load all cloud MCP connectors (v2.1.149)
pluginSuggestionMarketplaces list  — Managed setting allowlist for plugin marketplaces
enforceAvailableModels     bool    — Block model-list widening (v2.1.175)

## Tool Permissions Syntax
"Bash(git:*)"              — Bash commands matching prefix
"Tool(param:value)"        — Match by tool parameter (v2.1.178)
"Edit(src/**)"             — Glob in tool position
"WebFetch(domain.com)"     — Preapprove domains
