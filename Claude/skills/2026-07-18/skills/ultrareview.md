# /ultrareview

- Slug: `ultrareview`
- Command: `/ultrareview [PR#]`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user says "ultrareview" or wants multi-agent review

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/ultrareview` refusing to run in repos with no merge base — it now offers to
review all tracked files
