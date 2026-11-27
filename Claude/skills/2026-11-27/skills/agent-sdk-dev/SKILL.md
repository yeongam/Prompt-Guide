---
name: agent-sdk-dev
description: Scaffold or verify a Claude Agent SDK app (TS or Python). Use on "new Agent SDK app", "build an agent with the SDK".
---
# Agent SDK Dev
Src: claude-plugins-official/agent-sdk-dev@0fbfda5a91f4 (/new-sdk-app)
1. Ask/decide: language (TS|Python), name, agent purpose.
2. Install latest SDK (`@anthropic-ai/claude-agent-sdk` | `claude-agent-sdk`); check current version, never guess.
3. Scaffold minimal entry + `.env.example` (ANTHROPIC_API_KEY), typecheck/run.
4. Verify against SDK docs: options, tools, permissions, streaming; fix deviations.
Model ids: use latest family (see catalog `models`).
