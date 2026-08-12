# TypeScript SDK Compatibility Check

- Slug: `typescript-sdk-compatibility-check`
- Event: `pre_apply`
- Source: https://github.com/anthropics/claude-agent-sdk-typescript
- Source commit: `0a2639d6b561`
- Trigger: Run before applying TypeScript Agent SDK guidance or examples.

## Checks

1. Verify the TypeScript Agent SDK source commit used by the routine.
2. Keep generated guidance aligned with typed SDK usage.
3. Avoid duplicating Python-specific patterns in TypeScript output.

## Actions

- Attach commit evidence to TypeScript SDK skill output.
- Flag cross-language conflicts in the changelog conflict section.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

TypeScript/Node SDK for building agents on top of Claude Code
