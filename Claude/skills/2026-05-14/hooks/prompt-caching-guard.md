# Prompt Caching Guard

- Slug: `prompt-caching-guard`
- Event: `pre_apply`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source commit: `unknown`
- Trigger: Run before applying any skill that involves prompt caching.

## Checks

1. Confirm cache_control headers are attached to the correct message blocks.
2. Verify model supports prompt caching before emitting caching guidance.
3. Keep caching examples minimal and cache-breakage-free.

## Actions

- Record caching-related changes in the changelog token-savings section.
- Flag models that do not support caching in the conflict section.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or other AI directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Official Python library for the Anthropic API
