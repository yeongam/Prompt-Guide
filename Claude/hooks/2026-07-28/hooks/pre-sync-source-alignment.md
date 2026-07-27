# Pre Sync Source Alignment

- Slug: `pre-sync-source-alignment`
- Event: `pre_sync`
- Source: https://github.com/anthropics/anthropic-cookbook
- Source commit: `85016cacf5b7`
- Trigger: Run before generating Claude skills or hooks.

## Checks

1. Resolve the latest official Anthropic source commit.
2. Reject unofficial source material for generated artifacts.
3. Confirm skill and hook slugs are unique before writing files.

## Actions

- Record source URL, branch, and commit in each generated card.
- Use source summaries instead of copying long upstream content.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Examples and guides for using the Claude API
