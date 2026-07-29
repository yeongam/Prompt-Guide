# Task Created Tracker

- Slug: `task-created-tracker`
- Event: `TaskCreated`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires when a task is created via TaskCreate (added v2.1.90).

## Checks

1. Confirm task metadata is complete before logging.

## Actions

- Log/track task creation events.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
