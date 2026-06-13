# Python SDK Compatibility Check

- Slug: `python-sdk-compatibility-check`
- Event: `pre_apply`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source commit: `bootstrap-2026-06-13`
- Trigger: Run before applying Python SDK guidance or examples.

## Checks

1. Verify the Python SDK source commit used by the routine.
2. Prefer current SDK request shapes over stale snippets.
3. Keep migration notes compact and version-aware.

## Actions

- Attach commit evidence to Python SDK skill output.
- Flag incompatible examples in the changelog conflict section.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or other provider directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Official Python SDK for the Anthropic API.
