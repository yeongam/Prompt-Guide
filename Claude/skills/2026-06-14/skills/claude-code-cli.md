# Claude Code CLI

- Slug: `claude-code-cli`
- Source: https://github.com/anthropics/claude-code
- Source commit: `bootstrap-2026-06-13`
- Trigger: Use when implementing or extending Claude Code slash commands, hooks, or CLI features.

## Procedure

1. Check official Anthropic source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Compact Claude Code feature checklist with official-source alignment.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Claude Code CLI — the official agentic coding assistant by Anthropic.
