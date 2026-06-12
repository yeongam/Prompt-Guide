# Claude Code Agents & Workflows
# Source: anthropics/claude-code v2.1.175
# Updated: 2026-06-12

## Agent Commands
claude agents                    → List all sessions (Research Preview, v2.1.139)
claude agents --json             → Output live sessions as JSON; includes waitingFor field
claude agents --add-dir --settings --mcp-config --plugin-dir --permission-mode --model --effort
claude --bg --exec '<cmd>'       → Launch background session (v2.1.154)

## Sub-agent Nesting
- Up to 5 levels deep (v2.1.172)
- Dynamic workflows: orchestrate 10–100+ agents (v2.1.154)
- CLAUDE_CODE_SUBAGENT_MODEL → override sub-agent model

## Hooks Reference
PreToolUse      → Before tool execution; can block (exit 2 or JSON {decision:"block"})
PostToolUse     → After tool completes; cannot block
Notification    → Push-notification events
Stop            → After assistant turn; can return additionalContext (v2.1.163)
SubagentStop    → After subagent turn; can return additionalContext (v2.1.163)
PreCompact      → Before compaction; can block (v2.1.85)
TaskCreated     → On TaskCreate tool use (v2.1.90)
WorktreeCreate  → On worktree creation; HTTP type returns hookSpecificOutput.worktreePath
PermissionDenied → After auto-mode denial; return {retry:true} to re-run (v2.1.95)
MessageDisplay  → Transforms assistant message display (v2.1.152)
SessionStart    → Returns reloadSkills:true + sessionTitle (v2.1.152)

## Hook Invoke Types
shell     → default; shell command
mcp_tool  → invoke MCP tool directly (v2.1.118)
http      → HTTP endpoint (WorktreeCreate only)

## Hook JSON Fields
effort.level     → Current effort in hook JSON (v2.1.133)
args: string[]   → Exec-form shell-free execution (v2.1.140)
additionalContext → Feedback from Stop/SubagentStop (v2.1.163)
CLAUDE_EFFORT    → Effort level in Bash subprocess env

## Worktree Settings
worktree.baseRef: fresh|head → Branch base control (v2.1.133)
worktree.bgIsolation: none   → For repos where worktrees are impractical (v2.1.143)

## Token Policy
- Link to section by slug; avoid duplicating hook event tables
- Only emit changed/relevant hooks per query
