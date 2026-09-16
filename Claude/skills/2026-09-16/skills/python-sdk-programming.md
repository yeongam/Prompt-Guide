# Python SDK Programming

- Slug: `python-sdk-programming`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source ref: main (fetched 2026-09-16)
- Trigger: Use for Python SDK integration, request structure, and migration checks.

## Procedure

1. Check the official source for the current API/CLI shape before coding.
2. Prefer the smallest working implementation over speculative abstractions.
3. Use the SDK's structured types/tools instead of hand-rolled parsing.
4. Keep generated snippets short; link back to the source repo for depth.
5. Verify with the narrowest relevant command or test before finishing.

## Output

Minimal Claude Python SDK guidance with verification steps.

## Token Policy

- Avoid repeating background context already in the source repo.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs verbatim.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> # Claude SDK for Python The Claude SDK for Python provides access to the [Claude API](https://docs.anthropic.com/en/api/) from Python applications. ## Documentation Full documentation is available at **[platform.claude.com/docs/en/api/sdks/python](https://platform.claude.com/docs/en/api/sdks/python)**. ## Installation ```sh pip install anthropic ``` Upgrading from a `0.x` release? See the [v1 migration.
