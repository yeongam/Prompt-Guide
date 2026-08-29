# Session Stop Notification

- Slug: `session-stop-notification`
- Event: `Stop`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Fires after the assistant turn completes.

## Checks

1. Confirm the turn reached a terminal state.
2. Skip notification when nothing changed this turn.

## Actions

- Send a single compact status update.
- Avoid re-notifying for identical consecutive states.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Post-turn logging and notifications
