# Python Agent SDK Programming

- Slug: `python-agent-sdk-programming`
- Source: https://github.com/anthropics/claude-agent-sdk-python
- Source commit: `be2d0dfbd9ee`
- Trigger: Use for Python Claude Agent SDK integration and custom agent loops.

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Minimal Python Agent SDK guidance with verification steps.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude Agent SDK for Python Python SDK for Claude Agent. See the [Claude Agent SDK
documentation](https://platform.claude.com/docs/en/agent-sdk/python) for more
information. ## Installation **Prerequisites:** - Python 3.10+ **Note:** The Claude Code
CLI is automatically bundled with the package - no separate installation required! The
SDK will use the bundled CLI by default. If you prefer to use a system-wide inst.
