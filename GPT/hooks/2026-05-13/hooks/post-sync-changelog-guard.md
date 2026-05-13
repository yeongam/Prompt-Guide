# Post Sync Changelog Guard

- Slug: `post-sync-changelog-guard`
- Event: `post_sync`
- Source: https://github.com/openai/openai-cookbook
- Source commit: `923aaf288813`
- Trigger: Run after GPT skills and hooks are generated.

## Checks

1. Compare generated catalogs with the previous dated snapshot.
2. List added, modified, and deleted skills and hooks separately.
3. Confirm token-saving and conflict-resolution notes are present.

## Actions

- Write one concise changelog under GPT/Changelogs.
- Avoid prompting the user during automated routine execution.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify Claude or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Documentation and cookbook examples for OpenAI API workflows
