# Session Reference Guard

- Slug: `session-reference-guard`
- Event: `session_reference`
- Source: https://github.com/anthropics/claude-code
- Source commit: `bootstrap-2026-06-13`
- Trigger: Use when Claude Code works from Prompt-Guide/Claude routine output.

## Checks

1. Treat the latest Claude skills and hooks snapshots as repo-local guidance.
2. Do not assume GitHub Actions changed the live Claude Code runtime.
3. Keep local runtime installation separate from remote repo synchronization.

## Actions

- Apply the latest Claude guidance in the active session when relevant.
- Document any required local install step instead of silently editing runtime state.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or other provider directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Claude Code CLI — session reference and skills application.
