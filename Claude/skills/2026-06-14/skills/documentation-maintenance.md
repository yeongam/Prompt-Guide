# Documentation Maintenance

- Slug: `documentation-maintenance`
- Source: https://github.com/anthropics/anthropic-cookbook
- Source commit: `bootstrap-2026-06-13`
- Trigger: Use when updating docs, examples, prompts, or developer guides for Claude projects.

## Procedure

1. Check official Anthropic source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Concise documentation update checklist with source traceability.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Documentation and cookbook examples for Claude API workflows.
