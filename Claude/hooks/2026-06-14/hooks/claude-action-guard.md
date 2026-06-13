# Claude Action Guard

- Slug: `claude-action-guard`
- Event: `post_apply`
- Source: https://github.com/anthropics/claude-code-action
- Source commit: `bootstrap-2026-06-13`
- Trigger: Run after applying Claude Code GitHub Actions guidance.

## Checks

1. Confirm Actions integration stays separated from SDK guidance.
2. Prefer minimal working workflow patterns.
3. Preserve existing Claude skill behavior when adding Actions guidance.

## Actions

- Record Actions integration conflicts in the changelog.
- Keep Actions guidance short enough for fast reuse.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or other provider directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

GitHub Actions integration for Claude Code.
