# ultrareview

- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user says "ultrareview" or wants multi-agent review

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

## Note

Billed; requires git repo; no GitHub remote needed for local mode

