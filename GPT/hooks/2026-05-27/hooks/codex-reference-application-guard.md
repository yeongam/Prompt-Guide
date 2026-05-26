# Codex Reference Application Guard

- Slug: `codex-reference-application-guard`
- Event: `session_reference`
- Source: https://github.com/openai/codex
- Source commit: `b84c5898df75`
- Trigger: Use when Codex works from Prompt-Guide/GPT routine output.

## Checks

1. Treat the latest GPT skills and hooks snapshots as repo-local guidance.
2. Do not assume GitHub Actions changed the live Codex runtime.
3. Keep local runtime installation separate from remote repo synchronization.

## Actions

- Apply the latest GPT guidance in the active session when relevant.
- Document any required local install step instead of silently editing runtime state.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify Claude or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Lightweight coding agent that runs in the terminal
