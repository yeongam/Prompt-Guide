# Claude Code Commands (slash skills)
# Source: anthropics/claude-code v2.1.183
# Date: 2026-06-19

## Core Workflow
/init            — Generate CLAUDE.md (architecture, conventions, commands)
/review          — Multi-pass PR review (logic, style, security, tests)
/code-review     — Review with effort level; --comment posts inline; --fix applies findings
/security-review — OWASP audit of pending diffs; risk-ranked findings
/simplify        — Cleanup-only review with auto-apply (no bug hunt)
/effort [level]  — Adjust effort: faster / default / xhigh (Opus 4.8 = xhigh)

## Session & Config
/config [key=val] — Set settings from prompt; --help lists shorthand keys
/theme [name]    — Create or switch custom color themes
/color           — Set random session color
/tui             — Flicker-free alt-screen TUI rendering
/focus           — Toggle compact view (prompt + tool summary + response)
/undo            — Alias for /rewind; undoes last assistant action
/usage           — Token/cost stats (merged /cost + /stats)
/scroll-speed    — Tune mouse wheel speed with preview
/cd <dir>        — Move session to new working directory

## Agents & Workflows
/workflows       — View dynamic workflow runs
/goal <cond>     — Set turn-spanning completion condition
/loop [N] [/cmd] — Recurring task (default 10m); e.g. /loop 5m /review
/bg              — Send current task to background session
/resume          — Resume session (supports background sessions)
/diff            — Detail view with keyboard scrolling

## Plugins & Skills
/plugin list [--enabled|--disabled] — List plugins with filter
/plugin details <name>              — Show plugin inventory & token cost
/reload-skills   — Re-scan skill directories without restart

## Utilities
/chrome          — Select connected browser
/btw             — Inline note; "c" to copy preserving format
/model           — Switch model; "d" sets default
/mcp             — MCP server management
/doctor          — Diagnostics (flat tree layout)
/claude-api      — Build/debug Claude API apps (caching, tools, migration)
/ultrareview     — Parallel multi-agent cloud review (no-arg=local, arg=PR#)
/ultraplan       — Cloud worktrees for multi-agent planning
/team-onboarding — Generate onboarding guide from usage history
/powerup         — Interactive animated feature demos
/session-start-hook — Create SessionStart hook for test/lint runners
/update-config   — Configure settings.json (hooks, permissions, env vars)
/keybindings-help — Customize ~/.claude/keybindings.json
/fewer-permission-prompts — Add bash/MCP allowlist to settings.json
/claude-api      — Claude API reference (caching, tool use, model migration)
