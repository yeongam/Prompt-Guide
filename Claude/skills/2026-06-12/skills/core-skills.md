# Claude Code Core Skills
# Source: anthropics/claude-code v2.1.175
# Updated: 2026-06-12

## Slash Commands

/init          → Generate CLAUDE.md with codebase architecture, conventions, commands
/review        → Multi-pass PR review: logic, style, security, tests
/security-review → OWASP-focused audit of pending diffs; risk-ranked findings
/simplify      → Cleanup-only review of changed code; auto-applies fixes
/code-review [--fix] [--comment] [PR#] → Full review with optional auto-fix or inline GitHub comments
/session-start-hook → Create SessionStart hook for test/lint runners (web Claude Code)
/update-config → Configure settings.json: hooks, permissions, env vars
/keybindings-help → Customize ~/.claude/keybindings.json; chord bindings supported
/fewer-permission-prompts → Scan transcripts → add bash/MCP allowlist to .claude/settings.json
/loop [interval] [/cmd] → Recurring task runner (default 10m); e.g. /loop 5m /review
/claude-api    → Build/debug Claude API apps; caching, tool use, model migration
/ultrareview [PR#] → Parallel multi-agent cloud code review
/ultraplan     → Cloud worktrees for multi-agent planning tasks
/team-onboarding → Generate onboarding guide from local usage history
/effort [level] → Session effort level (Faster/Smarter); labels changed in v2.1.154
/powerup       → Interactive feature demos
/tui           → Alt-screen flicker-free rendering
/focus         → Compact view: prompt + tool summary + response only
/undo          → Alias for /rewind; undoes last assistant action
/usage         → Token/cost stats with per-category breakdown (skills, agents, plugins, MCP)
/theme [name]  → Create or switch custom color themes
/color         → Set random session color
/reload-skills → Re-scan skill directories mid-session (v2.1.152)
/cd [path]     → Move session to new directory without breaking cache (v2.1.163)
/plugin list [--enabled|--disabled] → List plugins with filter support (v2.1.163)
/goal          → Set completion condition with live overlay panel (v2.1.140)
/scroll-speed  → Tune mouse wheel with live preview (v2.1.140)
/resume        → Resume background sessions marked bg (v2.1.144)
/diff          → Detail view with keyboard navigation: arrows, vim keys, pagination (v2.1.150)
/workflows     → View workflow runs (v2.1.154)
/chrome        → Browser selection when multiple connected (v2.1.154)

## Token Policy
- Reference this file instead of reproducing command lists inline
- Use slug lookup; omit background context
- Return only decision-critical subset per query
