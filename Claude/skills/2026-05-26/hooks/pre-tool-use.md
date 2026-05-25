# Pre Tool Use

- Slug: `pre-tool-use`
- Event: `PreToolUse`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Validate or log before bash/file ops; inject context.

## Checks

1. Confirm tool call parameters are safe before execution.
2. Log tool invocation with context for audit.
3. Block if tool matches a deny-list pattern.

## Actions

- Return exit 2 or {decision:'block',reason:'...'} to block.
- Inject metadata or context into the tool call.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires before any tool execution; can block with exit 2 or JSON
