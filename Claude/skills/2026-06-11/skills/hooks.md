# Claude Code Hooks — 2026-06-11
# Source: anthropics/claude-code v2.1.173
# Block: exit 2 OR {decision:"block",reason:"..."}
# Retry: {retry:true} (PermissionDenied only)
# Conditional: add `if` field using permission rule syntax

## Lifecycle Hooks

| Hook            | Fires                              | Block | Added     | Use                                          |
|-----------------|------------------------------------|-------|-----------|----------------------------------------------|
| PreToolUse      | Before any tool execution          | yes   | core      | Validate/log before bash/file ops; inject ctx|
| PostToolUse     | After tool completes               | no    | core      | Log results, trigger follow-up actions       |
| Notification    | On push-notification events        | no    | core      | Forward alerts to mobile/Slack               |
| Stop            | After assistant turn completes     | no    | core      | Post-turn logging, notifications             |
| SubagentStop    | After subagent turn completes      | no    | core      | Subagent result aggregation                  |
| PreCompact      | Before conversation compaction     | yes   | v2.1.85   | Prevent compaction during critical ops       |
| TaskCreated     | When task created via TaskCreate   | no    | v2.1.90   | Log/track task creation events               |
| WorktreeCreate  | On worktree creation               | no    | v2.1.88   | Custom worktree provisioning via HTTP        |
| PermissionDenied| After auto-mode classifier denial  | no    | v2.1.95   | Custom permission escalation flows           |
| post-session    | After session ends (self-hosted)   | no    | v2.1.169  | Post-session cleanup on self-hosted runners  |

## Hook Output (v2.1.163+)
Stop and SubagentStop can return `hookSpecificOutput.additionalContext` to inject context.

## Invoke Types
- `shell`    — default; run shell command
- `mcp_tool` — invoke MCP tool directly [v2.1.118]
- `http`     — HTTP endpoint (WorktreeCreate only)
