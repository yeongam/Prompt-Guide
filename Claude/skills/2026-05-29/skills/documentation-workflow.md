# Documentation Workflow

- Slug: `documentation-workflow`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use for writing, updating, or maintaining technical documentation and developer guides.

## Procedure

1. Identify the audience: end-user, API developer, or contributor.
2. Link to source code instead of copying long code blocks.
3. Keep examples runnable and minimal.
4. Update changelog when removing or renaming public APIs.
5. Verify all commands and code samples before publishing.

## Output

Concise documentation update with source traceability.

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
