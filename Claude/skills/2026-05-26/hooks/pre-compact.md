# Pre Compact

- Slug: `pre-compact`
- Event: `PreCompact`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Prevent compaction during critical operations.

## Checks

1. Check if active operation is sensitive to context loss.
2. Verify compaction timing is safe.

## Actions

- Return {decision:'block'} or exit 2 to delay compaction.
- Log compaction attempt with current operation context.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires before conversation compaction; can block (added v2.1.85)
