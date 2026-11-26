---
name: claude-api
description: Build/debug/optimize Claude API or Agent SDK code. Use when code imports anthropic or user asks about Claude models/pricing/caching.
---
Models: claude-fable-5-2 | claude-opus-5-5 | claude-sonnet-5-5 | claude-haiku-5-5.
Subcommands of built-in `/claude-api`:
- `upgrade` — anthropic Python 0.x -> 1.x
- `api-version` — move to API version 2026-10-21
- `cost-optimize` / `latency-optimize` — measured one-lever-at-a-time changes
- `managed-agents-onboard <url|quickstart>` / `managed-agents-secure`
Rules: never answer model/pricing from memory; cache stable prefixes.
