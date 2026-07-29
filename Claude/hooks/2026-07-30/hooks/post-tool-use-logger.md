# Post Tool Use Logger

- Slug: `post-tool-use-logger`
- Event: `PostToolUse`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires after a tool call completes.

## Checks

1. Confirm the tool result matches expected shape.

## Actions

- Log results; trigger follow-up actions.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
