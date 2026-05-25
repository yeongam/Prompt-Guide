# Post Tool Use

- Slug: `post-tool-use`
- Event: `PostToolUse`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Log results or trigger follow-up actions after tool execution.

## Checks

1. Verify tool output for unexpected side effects.
2. Log result metadata for observability.

## Actions

- Forward tool result to external logging system.
- Trigger follow-up automation based on result.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires after tool completes; cannot block
