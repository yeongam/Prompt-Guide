# Claude Code CLI

- Slug: `claude-code-cli`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use for Claude Code CLI features, slash commands, hooks, MCP servers, and settings.

## Procedure

1. Check official Anthropic source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

CLI feature reference with hooks, settings, slash commands, and MCP guidance.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude Code ![](https://img.shields.io/badge/Node.js-18%2B-brightgreen?style=flat-
square) [![npm]](https://www.npmjs.com/package/@anthropic-ai/claude-code) [npm]:
https://img.shields.io/npm/v/@anthropic-ai/claude-code.svg?style=flat-square Claude Code
is an agentic coding tool that lives in your terminal, understands your codebase, and
helps you code faster by executing routine tasks, explaining complex code, and.
