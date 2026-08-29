# Pre Tool Use Guard

- Slug: `pre-tool-use-guard`
- Event: `PreToolUse`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Fires before bash/file/MCP tool execution.

## Checks

1. Confirm the tool call matches an allowed pattern.
2. Reject destructive commands outside declared scope.
3. Keep validation logic short-circuiting and side-effect free.

## Actions

- Block with exit code 2 or {decision:'block'} on violation.
- Inject minimal extra context only when required.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Validate or block before any tool executes
