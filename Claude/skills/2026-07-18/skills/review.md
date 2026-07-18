# /review

- Slug: `review`
- Command: `/review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/review` using a deprecated `projectCards` GraphQL query that errored on repos
with Classic Projects
