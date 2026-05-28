# Init — Codebase Initialization

- Slug: `init`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use when user asks to initialize, document, or audit codebase architecture.

## Procedure

1. Scan repo structure and identify key directories.
2. Detect framework, language, test runner, and lint commands.
3. Document observed conventions — don't invent them.
4. Keep CLAUDE.md under 300 lines; omit obvious things.
5. Verify documented commands actually run before writing.

## Output

CLAUDE.md with architecture, conventions, and verified commands.

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
