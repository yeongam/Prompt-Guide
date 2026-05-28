# Claude Code Automation — Hooks & Settings

- Slug: `claude-code-automation`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use for hooks (PreToolUse, PostToolUse, Stop, etc.), settings.json, and permissions.

## Procedure

1. Identify the lifecycle event: PreToolUse, PostToolUse, Stop, Notification, etc.
2. Write the hook as a shell command or MCP tool invocation.
3. To block: exit 2 or return JSON {decision:'block', reason:'...'}.
4. Place project hooks in .claude/settings.json, user hooks in ~/.claude/settings.json.
5. Test the hook with a benign tool call before enabling in production.

## Output

Working hook or settings block ready to paste into .claude/settings.json.

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
