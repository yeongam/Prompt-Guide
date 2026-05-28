# Code Review & Security Audit

- Slug: `code-review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: Use when user asks to review code, PR, branch, or run a security audit.

## Procedure

1. Read the full diff before forming opinions.
2. Rank findings: critical > high > medium > low.
3. Apply OWASP top-10 lens on user input and auth flows.
4. Suggest concrete fixes, not just observations.
5. Skip trivial style notes a linter can catch.

## Output

Risk-ranked findings: logic errors, security issues, style problems.

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
