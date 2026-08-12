# API Coding Guard

- Slug: `api-coding-guard`
- Event: `post_apply`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source commit: `009b035305e0`
- Trigger: Run after applying direct Claude API guidance.

## Checks

1. Confirm request/response shapes match the current SDK release.
2. Prefer minimal runnable examples over speculative usage.
3. Preserve existing Claude skill behavior when adding API guidance.

## Actions

- Record API guidance conflicts in the changelog.
- Keep API guidance short enough for fast reuse.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Official Python client for the Claude (Messages) API
