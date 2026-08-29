# Permission Denied Retry

- Slug: `permission-denied-retry`
- Event: `PermissionDenied`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Fires after the auto-mode permission classifier denies a call.

## Checks

1. Confirm the denial reason before requesting retry.
2. Cap retries to avoid classifier thrashing.

## Actions

- Return {retry:true} only for a corrected, narrower request.
- Surface unresolved denials instead of looping silently.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Custom permission escalation flow after auto-mode classifier denial
