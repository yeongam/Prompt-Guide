# Pre Compact Guard

- Slug: `pre-compact-guard`
- Event: `PreCompact`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Fires before automatic context compaction.

## Checks

1. Detect in-flight multi-step operations before compaction.
2. Block with exit code 2 or {decision:'block'} when unsafe.

## Actions

- Defer compaction until the current step commits.
- Log the deferred-compaction reason once, not repeatedly.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Prevent conversation compaction during critical operations
