# TypeScript Agent SDK Programming

- Slug: `typescript-agent-sdk-programming`
- Source: https://github.com/anthropics/claude-agent-sdk-typescript
- Source ref: `README.md` (branch `main`)
- CLI version context: 2.1.220
- Trigger: Use for building custom agents, tools, and hooks with the TypeScript Agent SDK.

## Procedure

1. Check the official source file for current behavior before answering.
2. Prefer the smallest working implementation.
3. Use structured APIs/config keys over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command or test.

## Output

Minimal TypeScript Agent SDK integration checklist.

## Token Policy

- Avoid repeated background context across turns.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude Agent SDK
![](https://img.shields.io/badge/Node.js-18%2B-brightgreen?style=flat-square)
[![npm]](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk) [npm]:
https://img.shields.io/npm/v/@anthropic-ai/claude-agent-sdk.svg?style=flat-square The
Claude Agent SDK enables you to programmatically build AI agents with Claude Code's
capabilities. Create autonomous agents that can understand codebases, edit.
