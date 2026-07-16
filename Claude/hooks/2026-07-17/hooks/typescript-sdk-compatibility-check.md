# TypeScript SDK Compatibility Check

- Slug: `typescript-sdk-compatibility-check`
- Event: `pre_apply`
- Source: https://github.com/anthropics/anthropic-sdk-typescript
- Source commit: `9e46760688a2`
- Trigger: Run before applying TypeScript SDK guidance or examples.

## Checks

1. Verify the TypeScript SDK source commit used by the routine.
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

Official JavaScript / TypeScript library for the Anthropic API
