# Release Notes

- Slug: `release-notes`
- Command: `/release-notes`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user asks what's new in Claude Code, or wants to see the changelog

## Summary

Shows Claude Code's release notes/changelog inline. Fixed to no longer inject
the full changelog history into the model's context on "Show all", and no
longer gets stuck on an old version after a failed changelog refresh.

## Token Policy

- Document-facing skill; keep responses to the relevant version range, not the whole history.

## Compatibility

- Purely informational; no interaction with other skills.
