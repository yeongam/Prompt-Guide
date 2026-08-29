# Post Sync Changelog Guard

- Slug: `post-sync-changelog-guard`
- Event: `post_sync`
- Source: https://github.com/anthropics/claude-code
- Source ref: `aa0d8b80ac08`
- Trigger: Runs after generating Claude skills or hooks for the day.

## Checks

1. Compare generated catalogs with the previous dated snapshot.
2. List added, modified, and deleted skills and hooks separately.
3. Confirm token-saving and conflict-resolution notes are present.

## Actions

- Write one concise changelog under Claude/Changelogs.
- Never prompt the user during automated routine execution.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Guard the daily Claude skill/hook sync routine itself
