# Reload Skills

- Slug: `reload-skills`
- Command: `/reload-skills`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user just added/edited skill files and wants them picked up without restarting the session

## Summary

Re-scans skill directories in place — no session restart required. Directly
relevant to this repo's own daily skill-sync routine: after `SKILLS_CATALOG.yaml`
or a dated skills snapshot changes, `/reload-skills` is the fastest way to
verify the update took effect in a live session.

## Token Policy

- One-line reference; this skill has no configuration surface worth restating.

## Compatibility

- Additive; no overlap with existing catalog entries.
