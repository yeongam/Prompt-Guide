# Skill Doctor

- Slug: `skill-doctor`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.261` (CHANGELOG.md)
- Trigger: User wants to audit loaded skills for unused ones or check their context-token cost.

## Procedure

1. Run `/skill-doctor` to list loaded skills with usage and context cost.
2. Flag skills that are loaded but never triggered.
3. Recommend disabling or scoping unused skills via `skillOverrides`.

## Output

Per-skill usage/cost table plus prune recommendations.

## Token Policy

- Use this before adding new skills to a project, not after.
- Prefer disabling over deleting when a skill may be needed later.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> Added `/skill-doctor` to show which loaded skills go unused and what they cost in context, so you can prune them.
