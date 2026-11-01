# claude-api
Use: code imports `anthropic`/`@anthropic-ai/sdk`, or Claude/LLM API questions. Never answer model/pricing from memory.
- Models: claude-fable-5-1, claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5.
- Subcmds: `api-version` (→2026-10-21) | `upgrade` (py anthropic 0.x→1.x; use anthropic.Timeout) | `cost-optimize` (caching, token hygiene, batch, effort, model; one measured change at a time) | `managed-agents-onboard <url|quickstart>` | `managed-agents-secure` (read-only audit).
- Tip: prompt caching + OTel tracing via `ant` CLI.
- Skip if project uses another provider.
