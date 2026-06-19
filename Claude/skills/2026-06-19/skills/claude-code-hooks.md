# Claude Code Hooks
# Source: anthropics/claude-code v2.1.183
# Date: 2026-06-19
# Block: exit 2 | {decision:"block",reason:"..."} | Retry (PermissionDenied): {retry:true}

PreToolUse      — Before any tool exec; can_block=true; inject context/validate
PostToolUse     — After tool; can_block=false; log/trigger follow-up
Notification    — Push events; forward to mobile/Slack
Stop            — After assistant turn; log/notify; returns additionalContext
SubagentStop    — After subagent turn; returns additionalContext + background_tasks + session_crons
PreCompact      — Before compaction; can_block=true; exit 2 or {decision:'block'}
TaskCreated     — On TaskCreate; log/track
WorktreeCreate  — On worktree creation; HTTP type returns hookSpecificOutput.worktreePath
EnterWorktree   — Switches between Claude-managed worktrees
PermissionDenied — After auto-mode denial; {retry:true} re-runs classifier
MessageDisplay  — Transforms assistant message text before display
post-session    — Lifecycle hook for self-hosted runners

## Invoke Types
shell    — Shell command (default); args: string[] spawns directly (exec form)
mcp_tool — Invoke MCP tool directly (v2.1.118+)
http     — HTTP endpoint (WorktreeCreate)

## Conditional Hooks
if: "Tool(param:value)"  — Match by tool parameter (v2.1.178)
if: "Edit(src/**)"       — Glob pattern (fixed v2.1.176)
if: "Bash($())"          — Variables in conditions (fixed v2.1.163)

## SessionStart Hook Outputs
reloadSkills: true             — Re-scan skill dirs after session start
hookSpecificOutput.sessionTitle — Set session title from hook
