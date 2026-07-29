# Pre Compact Guard

- Slug: `pre-compact-guard`
- Event: `PreCompact`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires before conversation compaction (added v2.1.85).

## Checks

1. Check whether a critical operation is mid-flight.

## Actions

- Block compaction via exit 2 or {decision:"block"} until safe.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
