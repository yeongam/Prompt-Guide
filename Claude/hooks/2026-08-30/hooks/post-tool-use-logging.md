# Post Tool Use Logging

- Slug: `post-tool-use-logging`
- Event: `PostToolUse`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Fires after any tool call finishes.

## Checks

1. Verify tool result before logging.
2. Avoid duplicate log entries for retried calls.

## Actions

- Append compact result summary to the run log.
- Chain follow-up automation only when explicitly configured.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Log results and trigger follow-up actions after a tool completes
