# Claude Code Skills Context
> Auto-updated daily from anthropics/claude-code — do not edit manually.
> Version: 2.1.132 | Updated: 2026-05-07

## Available Skills

### `/init`
**Trigger:** user asks to initialize or document codebase
Generate CLAUDE.md with codebase architecture, conventions, commands

### `/review`
**Trigger:** user asks to review PR or branch
Multi-pass PR review; checks logic, style, security, tests

### `/security-review`
**Trigger:** user asks security audit of current branch changes
OWASP-focused audit of pending diffs; outputs risk-ranked findings

### `/simplify`
**Trigger:** user asks to clean up or refactor changed code
Review changed code for reuse/quality/efficiency, then fix issues

### `/session-start-hook`
**Trigger:** user wants test/lint runners on session start (web Claude Code)
Create SessionStart hook ensuring project can run tests and linters

### `/update-config`
**Trigger:** automated behavior requests ("when X", "allow Y", "set Z=val")
Configure settings.json; handles hooks, permissions, env vars

### `/keybindings-help`
**Trigger:** user wants to remap keys or add chord shortcuts
Customize ~/.claude/keybindings.json; supports chord bindings

### `/fewer-permission-prompts`
**Trigger:** user wants fewer permission dialogs
Scan transcripts → add bash/MCP allowlist to .claude/settings.json

### `/loop [interval] [/command]`
**Trigger:** user wants recurring task (e.g. "check every 5m", "keep running X")
Run prompt or slash command on recurring interval (default 10m)

### `/claude-api`
**Trigger:** code imports anthropic SDK; user asks about Claude API features
Build/debug Claude API apps; prompt caching, tool use, model migration

### `/ultrareview [PR#]`
**Trigger:** user says "ultrareview" or wants multi-agent review
Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

### `/ultraplan`
**Trigger:** user wants cloud environment for complex planning
Auto-create cloud worktrees/environments for multi-agent planning tasks

### `/team-onboarding`
**Trigger:** user wants teammate ramp-up guide
Generate onboarding guide from local Claude Code usage history/data

### `/effort`
**Trigger:** user wants to adjust effort/quality level
Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

### `/powerup`
**Trigger:** user wants feature demos or to learn Claude Code features
Interactive animated feature demos with lessons

### `/tui`
**Trigger:** rendering looks flickery or user wants full-screen mode
Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

### `/focus`
**Trigger:** user wants compact view of conversation
Toggle focus view showing only: prompt + tool summary + final response

### `/undo`
**Trigger:** user wants to undo last action
Alias for /rewind; undoes last assistant action

### `/usage`
**Trigger:** user asks about token or cost statistics
Show token usage and cost stats (merged /cost + /stats)

### `/theme [name]`
**Trigger:** user wants to change or create visual theme
Create or switch custom color themes

### `/color`
**Trigger:** user wants a session color
Set random session color (no args = random pick)

## Token Optimization
- YAML catalog (single source) — ~30% fewer tokens than JSON/Markdown duplication
- Descriptions capped at one line; examples only where non-obvious

## Sync Info
- Catalog: `Claude/skills/SKILLS_CATALOG.yaml`
- Snapshot: `Claude/skills/2026-05-07/`
- Changelog: `Claude/Changelogs/`
- Commands: `.claude/commands/`
