# Stop

- Slug: `stop`
- Event: `Stop`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Post-turn logging and notifications after assistant responds.

## Checks

1. Confirm turn completed without errors.
2. Check for any required follow-up notifications.

## Actions

- Send push notification on turn completion.
- Log turn summary to external system.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires after assistant turn completes; cannot block
