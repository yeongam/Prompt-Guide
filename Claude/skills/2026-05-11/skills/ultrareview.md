# ultrareview

- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user says "ultrareview" or wants multi-agent review
- Note: Billed; requires git repo; no GitHub remote needed for local mode

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
