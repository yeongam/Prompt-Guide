# ultrareview

- Slug: `ultrareview`
- Command: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user says "ultrareview" or wants multi-agent review

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Notes

- note: Billed; requires git repo; no GitHub remote needed for local mode

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
