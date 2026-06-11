# Claude Code Settings — 2026-06-11
# Source: anthropics/claude-code v2.1.173
# Place in .claude/settings.json (project) or ~/.claude/settings.json (user)

## Settings Reference

| Key                          | Type              | Default | Added     | Description                                              |
|------------------------------|-------------------|---------|-----------|----------------------------------------------------------|
| skillOverrides               | off\|user-invocable-only\|name-only | — | v2.1.126 | Control skill visibility to model |
| autoScrollEnabled            | bool              | true    | v2.1.100  | Disable auto-scroll in fullscreen TUI mode              |
| showThinkingSummaries        | bool              | false   | v2.1.95   | Control thinking summary generation                     |
| disableSkillShellExecution   | bool              | false   | v2.1.98   | Disable inline shell execution within skill definitions |
| disableBundledSkills         | bool              | false   | v2.1.169  | Disable all built-in bundled skills                     |
| fallbackModel                | string\|string[]  | —       | v2.1.166  | Up to 3 fallback models tried in order on error         |
| prUrlTemplate                | string            | —       | v2.1.101  | Custom URL template for PR footer badge                 |
| requiredMinimumVersion       | string            | —       | v2.1.163  | Managed: enforce minimum Claude Code version            |
| requiredMaximumVersion       | string            | —       | v2.1.163  | Managed: enforce maximum Claude Code version            |
| sandbox.network.deniedDomains| list[string]      | —       | v2.1.85   | Block specific domains even when allowlists exist       |

## Env Vars

| Variable                            | Description                                                  |
|-------------------------------------|--------------------------------------------------------------|
| CLAUDE_EFFORT                       | Current effort level; usable in skill template strings       |
| CLAUDE_CODE_NO_FLICKER              | 1 = alt-screen flicker-free rendering (same as /tui)        |
| CLAUDE_CODE_USE_POWERSHELL_TOOL     | 1 = enable PowerShell tool (Windows opt-in preview)         |
| CLAUDE_STREAM_IDLE_TIMEOUT_MS       | Integer ms for streaming idle watchdog timeout              |
| OTEL_LOG_RAW_API_BODIES             | 1 = emit full API request/response bodies as OTEL events    |
| DISABLE_UPDATES                     | 1 = block all update paths including manual 'claude update' |
| CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY | 1 = opt-in gateway /v1/models discovery             |

## Models (v2.1.173)

| Role    | Model ID                      | Notes                                |
|---------|-------------------------------|--------------------------------------|
| default | claude-sonnet-4-6             |                                      |
| opus    | claude-opus-4-7               | Fast mode; Max subscribers auto mode |
| sonnet  | claude-sonnet-4-6             |                                      |
| haiku   | claude-haiku-4-5-20251001     |                                      |
| fable   | claude-fable-5                | Mythos-class; added v2.1.170         |
