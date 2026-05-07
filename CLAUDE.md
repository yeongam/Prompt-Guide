# Skills v2.1.132 (2026-05-07)
> auto-updated from anthropics/claude-code — do not edit

`/init` | user asks to initialize or document codebase → Generate CLAUDE.md with codebase architecture, conventions, commands
`/review` | user asks to review PR or branch → Multi-pass PR review; checks logic, style, security, tests
`/security-review` | user asks security audit of current branch changes → OWASP-focused audit of pending diffs; outputs risk-ranked findings
`/simplify` | user asks to clean up or refactor changed code → Review changed code for reuse/quality/efficiency, then fix issues
`/session-start-hook` | user wants test/lint runners on session start (web Claude Code) → Create SessionStart hook ensuring project can run tests and linters
`/update-config` | automated behavior requests ("when X", "allow Y", "set Z=val") → Configure settings.json; handles hooks, permissions, env vars
`/keybindings-help` | user wants to remap keys or add chord shortcuts → Customize ~/.claude/keybindings.json; supports chord bindings
`/fewer-permission-prompts` | user wants fewer permission dialogs → Scan transcripts → add bash/MCP allowlist to .claude/settings.json
`/loop [interval] [/command]` | user wants recurring task (e.g. "check every 5m", "keep running X") → Run prompt or slash command on recurring interval (default 10m)
`/claude-api` | code imports anthropic SDK; user asks about Claude API features → Build/debug Claude API apps; prompt caching, tool use, model migration
`/ultrareview [PR#]` | user says "ultrareview" or wants multi-agent review → Parallel multi-agent cloud code review; billed; no-arg=local, arg=GitHub PR
`/ultraplan` | user wants cloud environment for complex planning → Auto-create cloud worktrees/environments for multi-agent planning tasks
`/team-onboarding` | user wants teammate ramp-up guide → Generate onboarding guide from local Claude Code usage history/data
`/effort` | user wants to adjust effort/quality level → Interactive slider for session effort level
`/powerup` | user wants feature demos or to learn Claude Code features → Interactive animated feature demos with lessons
`/tui` | rendering looks flickery or user wants full-screen mode → Switch to flicker-free alt-screen TUI rendering
`/focus` | user wants compact view of conversation → Toggle focus view showing only: prompt + tool summary + final response
`/undo` | user wants to undo last action → Rewind last assistant action
`/usage` | user asks about token or cost statistics → Show token usage and cost stats
`/theme [name]` | user wants to change or create visual theme → Create or switch custom color themes
`/color` | user wants a session color → Set random session color

catalog: Claude/skills/SKILLS_CATALOG.yaml | commands: .claude/commands/
