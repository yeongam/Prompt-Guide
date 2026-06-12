# Claude Code Settings & Config
# Source: anthropics/claude-code v2.1.175
# Updated: 2026-06-12

## Models
claude-fable-5              → Fable 5 (Mythos-class, v2.1.170)
claude-opus-4-8             → Opus 4.8; defaults /effort xhigh (v2.1.154)
claude-opus-4-7             → Opus 4.7; Fast mode default
claude-sonnet-4-6           → Sonnet 4.6 (session default)
claude-haiku-4-5-20251001   → Haiku 4.5

Note: Fable 5 [1m] suffix auto-normalized (v2.1.173)

## Settings (settings.json)
skillOverrides: off|user-invocable-only|name-only   → Skill exposure control (v2.1.126)
disableBundledSkills: bool    → Disable all built-in skills (v2.1.163)
fallbackModel: [m1,m2,m3]    → Up to 3 fallback models; --fallback-model flag (v2.1.166)
enforceAvailableModels: bool  → Constrain default model; prevent allowlist widening (v2.1.175)
wheelScrollAccelerationEnabled: bool → Disable wheel acceleration in fullscreen (v2.1.174)
autoScrollEnabled: bool       → Auto-scroll in fullscreen TUI (v2.1.100)
showThinkingSummaries: bool   → Thinking summary generation (default false, v2.1.95)
disableSkillShellExecution: bool → Disable inline shell in skill defs (v2.1.98)
prUrlTemplate: string         → Custom PR footer badge URL (v2.1.101)
sandbox.network.deniedDomains: list[string] → Block domains in broader allowlists (v2.1.85)
sandbox.bwrapPath / sandbox.socatPath → Custom binary paths (v2.1.133)
acceptEdits: bool             → Safer automated edit mode (v2.1.160)
parentSettingsBehavior: first-wins|merge → Admin key for settings merge (v2.1.133)
settings.autoMode.hard_deny   → Unconditional blocks in auto-mode (v2.1.139)
pluginSuggestionMarketplaces  → Managed allowlist for plugin suggestions (v2.1.152)
allowAllClaudeAiMcps: bool    → Enterprise managed MCP setting (v2.1.150)
requiredMinimumVersion        → Enforce minimum Claude Code version (v2.1.163)
requiredMaximumVersion        → Enforce maximum Claude Code version (v2.1.163)

## Environment Variables
ANTHROPIC_DEFAULT_SONNET_MODEL     → Override default Sonnet model (v2.1.174)
CLAUDE_CODE_SUBAGENT_MODEL         → Sub-agent model override (v2.1.147)
CLAUDE_CODE_SESSION_ID             → Session ID in stdio MCP + Bash env (v2.1.132/154)
CLAUDE_PROJECT_DIR                 → Project dir in MCP/hook envs (v2.1.140/154)
CLAUDE_EFFORT                      → Current effort level in template strings
CLAUDE_CODE_NO_FLICKER             → 1 = alt-screen rendering (same as /tui)
CLAUDE_CODE_USE_POWERSHELL_TOOL    → 1 = PowerShell tool (Windows preview)
CLAUDE_CODE_DISABLE_BUNDLED_SKILLS → Disable built-in skills (v2.1.163)
CLAUDE_CODE_STOP_HOOK_BLOCK_CAP    → Max stop-hook blocks (default 8, v2.1.147)
CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN → 1 = native scrollback mode (v2.1.132)
CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL → Re-enable surveys for OTel (v2.1.139)
CLAUDE_CODE_PLUGIN_PREFER_HTTPS    → SSH→HTTPS cloning (v2.1.141)
CLAUDE_STREAM_IDLE_TIMEOUT_MS      → Streaming idle watchdog timeout (ms)
OTEL_LOG_RAW_API_BODIES            → 1 = full API bodies as OTEL events
OTEL_LOG_TOOL_DETAILS              → Tool parameter telemetry (v2.1.161)
OTEL_RESOURCE_ATTRIBUTES           → Included as metric labels (v2.1.161)
DISABLE_UPDATES                    → 1 = block all update paths
CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY → 1 = gateway /v1/models discovery
ANTHROPIC_WORKSPACE_ID             → Workload identity federation (v2.1.141)
CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE → Override fast mode base (v2.1.142)

## Plugin Commands
claude plugin init <name>  → Scaffold new plugin (v2.1.141)
claude plugin disable      → Refuses if other plugins depend on it (v2.1.143)
Plugins auto-load from .claude/skills directories (v2.1.141)
Root-level SKILL.md surfaces as skill (v2.1.142)
defaultEnabled: false in plugin.json → opt-out default (v2.1.154)
MCP skills can set disallowed-tools frontmatter (v2.1.152)

## Token Policy
- Return only the section(s) relevant to the query
- Skip version tags when token budget is tight
- Never reproduce full table when a single lookup suffices
