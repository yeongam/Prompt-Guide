# Claude Code Env Vars & Models
# Source: anthropics/claude-code v2.1.183
# Date: 2026-06-19

## Environment Variables
CLAUDE_EFFORT                              — Current effort level; usable in skill templates
CLAUDE_CODE_NO_FLICKER                     — 1 = alt-screen rendering (same as /tui)
CLAUDE_CODE_USE_POWERSHELL_TOOL            — 1 = enable PowerShell tool (Windows preview)
CLAUDE_STREAM_IDLE_TIMEOUT_MS              — Integer ms for streaming idle watchdog
OTEL_LOG_RAW_API_BODIES                    — 1 = emit full API bodies as OTEL events
OTEL_LOG_TOOL_DETAILS                      — 1 = include tool_parameters in OTEL spans
OTEL_RESOURCE_ATTRIBUTES                   — Labels for metric datapoints
DISABLE_UPDATES                            — 1 = block all update paths
CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY — 1 = opt-in gateway /v1/models discovery
CLAUDE_CODE_ENABLE_AUTO_MODE               — 1 = auto mode on Bedrock/Vertex/Foundry (v2.1.158)
CLAUDE_CLIENT_PRESENCE_FILE               — Path; suppresses mobile push notifications (v2.1.181)
CLAUDE_CODE_SAFE_MODE                      — 1 = disable all customizations (v2.1.169)
CLAUDE_CODE_PLUGIN_PREFER_HTTPS            — 1 = prefer HTTPS for plugin connections (v2.1.141)
CLAUDE_CODE_SUBAGENT_MODEL                 — Override model for subagents (v2.1.141)
CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY — 1 = opt out of bypass (v2.1.143)
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS       — 1 = spawn teammates via Agent name param (v2.1.178)
ANTHROPIC_WORKSPACE_ID                     — Workload identity workspace (v2.1.141)
MAX_THINKING_TOKENS                        — 0 = disable thinking on default models
CLAUDE_CODE_SESSION_ID                     — Passed to MCP stdio servers on --resume

## Models
default : claude-sonnet-4-6
opus    : claude-opus-4-8    # Auto mode; fast mode; xhigh effort default
sonnet  : claude-sonnet-4-6
haiku   : claude-haiku-4-5-20251001
fable5  : claude-fable-5     # Mythos-class; general use (v2.1.170)

## Subagent Depth Limit
Max nesting: 5 levels (v2.1.181)
