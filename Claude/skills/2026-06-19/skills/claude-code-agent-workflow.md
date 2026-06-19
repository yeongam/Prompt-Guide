# Claude Code Agent & Workflow Features
# Source: anthropics/claude-code v2.1.183
# Date: 2026-06-19

## Agent Teams (v2.1.178)
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 enables teammates via Agent tool name param.
Subagents nest up to 5 levels deep. claude agents view lists all sessions.

## Background Sessions
claude --bg         — Start background session
claude agents       — View/manage all sessions; --json outputs JSON with waitingFor
claude agents ! cmd — Run shell command as background session
Ctrl+T              — Pin background session (stays alive across updates)

## Plugins
claude plugin init <name>      — Scaffold new plugin
claude plugin enable <name>    — Force-enable with dependencies
claude plugin details <name>   — Show inventory, token cost, components
/plugin list --enabled/--disabled — Filtered listing
/plugin browse                 — Discover; Discover tab pins relevant plugins
defaultEnabled: false          — Plugin opt-in declaration
pluginSuggestionMarketplaces   — Managed allowlist for marketplaces

## Nested Skills (v2.1.178)
Skills in nested .claude/skills/ directories auto-load.
Closest .claude/ to working directory wins on collision.
Directory-qualified names resolve conflicts.
/reload-skills rescans without restart.

## Workflows (v2.1.154)
Dynamic workflows orchestrate work across hundreds of agents.
/workflows views runs. Workflow prompt keyword triggers on explicit phrases.

## Permission Rule Syntax (v2.1.178)
Tool(param:value) — Match specific tool parameter values
Example: Agent(model:opus) — Only when Agent uses opus model
Example: Bash(git:push)    — Only git push commands

## Safe Mode (v2.1.169)
--safe-mode flag or CLAUDE_CODE_SAFE_MODE=1 disables all customizations.
Useful for debugging or locked-down environments.

## Auto Mode Safety (v2.1.183)
Blocks destructive git commands and terraform destroy unless explicitly requested.
Auto mode classifier evaluates subagent spawns before launch.
Data exfiltration detection enabled.
