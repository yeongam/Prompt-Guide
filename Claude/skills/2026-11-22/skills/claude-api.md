---
name: claude-api
description: Build, debug, migrate or optimize Claude API / Anthropic SDK code. Use when code imports anthropic/@anthropic-ai or the task is LLM-shaped with no other provider.
---
Cmd: `/claude-api [sub]`
Subs: `upgrade` (py anthropic 0.x→1.x; timeouts = anthropic.Timeout) · `api-version` (→2026-10-21) ·
`cost-optimize` · `latency-optimize` · `prompt-audit` · `managed-agents-onboard <url|quickstart>` · `managed-agents-secure`
Rules:
- Models: claude-opus-5-5 | claude-sonnet-5-5 | claude-haiku-5-5 | claude-fable-5-2. Never answer pricing/limits from memory.
- Tokens: cache stable prefix (system+tools); keep tool defs stable; batch non-urgent; lower effort before smaller model.
- Change one lever at a time and measure against an eval.
Skip if OpenAI/Gemini/other provider is in use.
