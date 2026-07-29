# Permission Denied Escalation

- Slug: `permission-denied-escalation`
- Event: `PermissionDenied`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires after an auto-mode classifier denial (added v2.1.95).

## Checks

1. Confirm escalation criteria before requesting a retry.

## Actions

- Return {"retry": true} to re-run the classifier when appropriate.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
