# Subagent Stop

- Slug: `subagent-stop`
- Event: `SubagentStop`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Aggregate subagent results after subagent turn completes.

## Checks

1. Verify subagent output is complete.
2. Check for errors in subagent execution.

## Actions

- Aggregate subagent result into parent context.
- Log subagent completion metrics.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires after subagent turn completes; cannot block
