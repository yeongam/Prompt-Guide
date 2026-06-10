# Hooks Configuration

- Slug: `hooks-configuration`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.170`
- Trigger: Use for setting up lifecycle hooks, permission flows, and event-driven automation.

## Procedure

1. Identify lifecycle event (PreToolUse, PostToolUse, Stop, etc.).
2. Choose invoke type: shell | mcp_tool | http.
3. Block with `exit 2` or `{"decision":"block","reason":"..."}`.
4. Retry (PermissionDenied only) with `{"retry":true}`.
5. Test hook in isolation before enabling globally.

## Output

Minimal hook definition with event, type, and command/tool.

## Token Policy

- Return only the hook definition block; skip boilerplate.
- Use shell invoke type by default unless MCP tool is required.
- Omit conditional `if` field unless filtering is needed.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Hooks Reference (v2.1.129 → v2.1.170)

### Newly Added
| Hook | Added | Notes |
|------|-------|-------|
| `MessageDisplay` | v2.1.152 | Transform or hide assistant messages before display; can_block=true |
| `post-session` | v2.1.169 | Self-hosted runner: runs after session ends, before workspace deleted |

### Existing
| Hook | Fires | Block |
|------|-------|-------|
| `PreToolUse` | Before any tool | yes |
| `PostToolUse` | After tool completes | no |
| `Notification` | On push-notification events | no |
| `Stop` | After assistant turn | no |
| `SubagentStop` | After subagent turn | no |
| `PreCompact` | Before conversation compaction | yes |
| `TaskCreated` | On TaskCreate tool use | no |
| `WorktreeCreate` | On worktree creation | no |
| `PermissionDenied` | After auto-mode denial | no (retry) |

### Invoke Types
- `shell` — default; runs shell command
- `mcp_tool` — invoke MCP tool directly (v2.1.118+)
- `http` — HTTP endpoint (WorktreeCreate only)
- `args` exec form — spawn without shell (v2.1.139+); avoids quoting issues
