# Claude Code CLI Programming

- Slug: `claude-code-cli-programming`
- Source: https://github.com/anthropics/claude-code
- Source ref: `README.md` (branch `main`)
- CLI version context: 2.1.220
- Trigger: Use for CLI usage, slash commands, hooks, settings.json, and session config work.

## Procedure

1. Check the official source file for current behavior before answering.
2. Prefer the smallest working implementation.
3. Use structured APIs/config keys over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command or test.

## Output

Compact CLI/config checklist aligned to the current CHANGELOG version.

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

# Claude Code ![](https://img.shields.io/badge/Node.js-18%2B-brightgreen?style=flat-
square) [![npm]](https://www.npmjs.com/package/@anthropic-ai/claude-code) [npm]:
https://img.shields.io/npm/v/@anthropic-ai/claude-code.svg?style=flat-square Claude Code
is an agentic coding tool that lives in your terminal, understands your codebase, and
helps you code faster by executing routine tasks, explaining complex code, and.
