# Permission Denied

- Slug: `permission-denied`
- Event: `PermissionDenied`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Custom permission escalation flows after classifier denial.

## Checks

1. Identify which classifier rule triggered the denial.
2. Determine if escalation or retry is appropriate.

## Actions

- Return {retry:true} to re-run the classifier.
- Escalate to user or log denial reason.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires after auto-mode classifier denial; supports retry (added v2.1.95)
