# Task Created

- Slug: `task-created`
- Event: `TaskCreated`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Log or track task creation events.

## Checks

1. Verify task parameters are valid.
2. Check for duplicate task creation.

## Actions

- Log task creation with ID and parameters.
- Notify external task tracker.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires when task created via TaskCreate tool; cannot block (added v2.1.90)
