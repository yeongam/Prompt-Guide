# Notification

- Slug: `notification`
- Event: `Notification`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Forward alerts to mobile/Slack (requires Remote Control setup).

## Checks

1. Verify notification payload is valid.
2. Check notification routing configuration.

## Actions

- Route notification to configured channels (Slack, mobile, email).
- Log notification delivery status.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires on push-notification events; cannot block
