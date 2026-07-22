# Skill Authoring Guard

- Slug: `skill-authoring-guard`
- Event: `post_apply`
- Source: https://github.com/anthropics/skills
- Source ref (content fingerprint): `2fb9c4cc0263`
- Trigger: Run after applying skill-authoring guidance.

## Checks

1. Confirm new skills declare trigger, procedure, and output separately.
2. Prefer minimal runnable skill patterns.
3. Preserve existing Claude skill behavior when adding new guidance.

## Actions

- Record skill-authoring conflicts in the changelog.
- Keep skill guidance short enough for fast reuse.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Official example skills and skill-authoring documentation for Claude
