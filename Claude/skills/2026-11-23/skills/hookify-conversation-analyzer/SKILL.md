---
name: hookify-conversation-analyzer
description: "Use this agent when analyzing conversation transcripts to find behaviors worth preventing with hooks. Typical triggers include the /hookify command being invoked without arguments, or the user explic…"
---
`agent` · plugin `hookify`
Src: https://github.com/anthropics/claude-plugins-official/blob/65adb96f26de/plugins/hookify/agents/conversation-analyzer.md
Tools: ["Read", "Grep"]
Outline (full text at Src):
1. When to invoke
2. Read and analyze user messages to find frustration signals
3. Identify specific tool usage patterns that caused issues
4. Extract actionable patterns that can be matched with regex
5. Categorize issues by severity and type
