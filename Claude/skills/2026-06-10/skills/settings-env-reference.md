# Settings & Environment Reference

- Slug: `settings-env-reference`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.170`
- Trigger: Use for configuring settings.json keys or environment variables in Claude Code.

## Procedure

1. Prefer project `.claude/settings.json` over global `~/.claude/settings.json`.
2. Apply minimal required keys; avoid speculative config.
3. Validate version compatibility before using new settings.
4. Use env vars for runtime overrides; use settings.json for persistent config.
5. Test with `claude --safe-mode` if customizations cause issues.

## Output

Setting key with type, default, and added-version tag.

## Token Policy

- List only keys relevant to the task.
- Omit description if key name is self-explanatory.
- Skip version tags when context is clearly current.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Settings (New in v2.1.130–v2.1.170)

| Key | Type | Added | Description |
|-----|------|-------|-------------|
| `disableBundledSkills` | bool | v2.1.170 | Hide bundled skills and built-in slash commands |
| `fallbackModel` | list[str] | v2.1.166 | Up to 3 fallback models on primary failure |
| `requiredMinimumVersion` | str | v2.1.163 | Enforce minimum Claude Code version |
| `requiredMaximumVersion` | str | v2.1.163 | Enforce maximum Claude Code version |
| `parentSettingsBehavior` | str | v2.1.154 | `merge` or `first-wins` policy inheritance |
| `allowAllClaudeAiMcps` | bool | v2.1.154 | Load claude.ai MCP connectors with managed config |
| `worktree.baseRef` | str | v2.1.154 | Worktree branch source: `fresh` or `head` |
| `pluginSuggestionMarketplaces` | list | v2.1.152 | Allowlist org marketplaces for plugin suggestions |
| `disallowed-tools` | list | v2.1.152 | Remove tools while a skill is active |
| `worktree.bgIsolation` | str | v2.1.133 | `none` = allow background edits |
| `sandbox.bwrapPath` | str | v2.1.133 | Custom bubblewrap binary path |
| `sandbox.socatPath` | str | v2.1.133 | Custom socat binary path |

## Existing Settings (v2.1.129 and earlier)

`skillOverrides` `autoScrollEnabled` `showThinkingSummaries`
`disableSkillShellExecution` `prUrlTemplate` `sandbox.network.deniedDomains`

## Environment Variables (New in v2.1.130–v2.1.170)

| Var | Added | Description |
|-----|-------|-------------|
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` | v2.1.170 | Disable bundled skills; mirrors `disableBundledSkills` |
| `API_FORCE_IDLE_TIMEOUT` | v2.1.169 | Set `0` to disable idle timeout on Vertex/Foundry |
| `CLAUDE_CODE_SAFE_MODE` | v2.1.169 | Disable all customizations for troubleshooting |
| `CLAUDE_CODE_SESSION_ID` | v2.1.157 | Session identifier exposed to subprocess environment |
| `CLAUDE_CODE_EFFORT_LEVEL` | v2.1.154 | Override effort level; mirrors `/effort` |
| `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` | v2.1.147 | Configure stop-hook block retry limit |
| `ANTHROPIC_WORKSPACE_ID` | v2.1.141 | Scope minted token to specific workspace |
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | v2.1.141 | Clone plugins via HTTPS instead of SSH |
| `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` | v2.1.132 | Use native terminal scrollback instead of alt-screen |

## Existing Env Vars

`CLAUDE_EFFORT` `CLAUDE_CODE_NO_FLICKER` `CLAUDE_CODE_USE_POWERSHELL_TOOL`
`CLAUDE_STREAM_IDLE_TIMEOUT_MS` `OTEL_LOG_RAW_API_BODIES` `DISABLE_UPDATES`
`CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY`
