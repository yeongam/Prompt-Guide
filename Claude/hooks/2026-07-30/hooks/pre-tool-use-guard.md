# Pre Tool Use Guard

- Slug: `pre-tool-use-guard`
- Event: `PreToolUse`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires before any tool execution.

## Checks

1. Validate or log the pending bash/file operation.

## Actions

- Block with exit 2 or {decision:"block"}; inject context if needed.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
