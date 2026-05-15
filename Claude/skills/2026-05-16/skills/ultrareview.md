# ultrareview

- Cmd: `/ultrareview [PR#]`
- Trigger: user says 'ultrareview' or wants multi-agent cloud review
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
