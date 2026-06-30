# Post Tool Use

- Slug: `PostToolUse`
- Event: `PostToolUse`
- Can block: no
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.196`
- Source commit: `c80896ca84bd`

## Fires

After tool completes

## Use

Log results, trigger follow-up actions after tool runs

## Invoke Types

- `shell`
- `mcp_tool`
- `http`

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.
