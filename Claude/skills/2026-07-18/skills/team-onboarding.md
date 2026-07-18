# /team-onboarding

- Slug: `team-onboarding`
- Command: `/team-onboarding`
- Category: docs
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants teammate ramp-up guide

## Description

Generate onboarding guide from local Claude Code usage history/data

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Added `/team-onboarding` command to generate a teammate ramp-up guide from your local
Claude Code usage
