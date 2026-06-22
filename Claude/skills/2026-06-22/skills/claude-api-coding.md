---
name: Claude API Coding
slug: claude-api-coding
cmd: /claude-api
version: 2.1.185
trigger: Use when user asks about Claude API, Anthropic SDK, model IDs, pricing, tool use, streaming, caching, or agents.
---

Reference for Claude API / Anthropic SDK: model IDs, params, streaming, tool use, MCP, agents, caching, token counting.

**Current models:**
- Fable 5: `claude-fable-5` (Mythos-class, GA v2.1.170)
- Opus 4.8: `claude-opus-4-8`
- Sonnet 4.6: `claude-sonnet-4-6`
- Haiku 4.5: `claude-haiku-4-5-20251001`

**Key patterns:**
- Always use latest model IDs; check for deprecation warnings on stderr
- Prompt caching: `cache_control: {type: "ephemeral"}` on large context blocks
- Tool use: define tools in `tools[]`; handle `tool_use` stop reason
- Streaming: use `stream=True`; handle `message_delta` events
- Multi-agent: subagents can spawn subagents up to 5 levels deep (v2.1.172)

**Token policy:** Link to official docs; avoid copying long API reference text.
