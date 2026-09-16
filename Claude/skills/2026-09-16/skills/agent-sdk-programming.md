# Agent SDK Programming

- Slug: `agent-sdk-programming`
- Source: https://github.com/anthropics/claude-agent-sdk-python
- Source ref: main (fetched 2026-09-16); TS variant: anthropics/claude-agent-sdk-typescript
- Trigger: Use for building agents/tools/workflows with the Claude Agent SDK.

## Procedure

1. Check the official source for the current API/CLI shape before coding.
2. Prefer the smallest working implementation over speculative abstractions.
3. Use the SDK's structured types/tools instead of hand-rolled parsing.
4. Keep generated snippets short; link back to the source repo for depth.
5. Verify with the narrowest relevant command or test before finishing.

## Output

Lean agent workflow design and implementation checklist.

## Token Policy

- Avoid repeating background context already in the source repo.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs verbatim.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> # Claude Agent SDK for Python Python SDK for Claude Agent. See the [Claude Agent SDK documentation](https://platform.claude.com/docs/en/agent-sdk/python) for more information. ## Installation ```bash pip install claude-agent-sdk ``` **Prerequisites:** - Python 3.10+ **Note:** The Claude Code CLI is automatically bundled with the package - no separate installation required! The SDK will use the bundled CLI by.
