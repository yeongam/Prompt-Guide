# Claude Code Commands — 2026-06-11
# Source: anthropics/claude-code v2.1.173
# Format: cmd | trigger | desc

## Core Development
/init           | initialize/document codebase          | Generate CLAUDE.md with architecture, conventions, commands
/review         | review PR or branch                   | Multi-pass PR review; logic, style, security, tests
/security-review| security audit of branch changes      | OWASP-focused audit of pending diffs; risk-ranked findings
/simplify       | clean up or refactor changed code     | Review changed code for reuse/quality/efficiency, apply fixes
/code-review    | code review at given effort level     | Review diff for bugs/cleanups; --comment posts inline, --fix applies

## AI & Research
/claude-api     | anthropic SDK / Claude API questions  | Build/debug Claude API apps; caching, tool use, model migration
/deep-research  | multi-source fact-checked research    | Fan-out searches, fetch, verify, synthesize cited report
/ultrareview [PR#]| multi-agent review                | Parallel cloud code review; no-arg=local branch, arg=GitHub PR
/ultraplan      | complex multi-agent planning          | Auto-create cloud worktrees for multi-agent planning tasks

## Configuration
/update-config  | automated behavior / "when X" / allow | Configure settings.json; hooks, permissions, env vars
/session-start-hook| test/lint runners on session start| Create SessionStart hook for web Claude Code
/keybindings-help| remap keys or chord shortcuts       | Customize ~/.claude/keybindings.json
/fewer-permission-prompts| reduce permission dialogs  | Scan transcripts → add allowlist to .claude/settings.json

## Session Control
/effort         | adjust effort/quality level           | Interactive effort slider (also: CLAUDE_EFFORT env var)
/loop [interval] [/cmd]| recurring task                | Run command on interval; default 10m (e.g. /loop 5m /review)
/cd [path]      | move session to directory             | Change working directory without breaking prompt cache [v2.1.169]
/undo           | undo last action                      | Alias for /rewind; undoes last assistant action
/focus          | compact conversation view             | Toggle: show only prompt + tool summary + final response
/tui            | flickery rendering / full-screen      | Switch to flicker-free alt-screen TUI rendering

## UI & Appearance
/theme [name]   | change or create visual theme         | Create or switch custom color themes
/color          | session color                         | Set random session color
/usage          | token or cost statistics              | Show token usage and cost stats

## Onboarding & Discovery
/powerup        | feature demos / learn Claude Code     | Animated interactive feature demos with lessons
/team-onboarding| teammate ramp-up guide                | Generate onboarding from local Claude Code usage history

## Plugins & Workflows
/plugin list    | see installed plugins                 | List plugins with --enabled/--disabled filter [v2.1.163]
/workflows      | manage workflows                      | Open workflows panel (available during in-progress turns) [v2.1.169]
/voice          | voice mode                            | Toggle voice input/output

## App Testing
/run            | run or start the app                  | Launch project app to verify changes in real environment
/verify         | confirm a change works                | Run app and observe behavior to validate fix or feature
