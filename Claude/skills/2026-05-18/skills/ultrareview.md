# ultrareview

- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user says "ultrareview" or wants multi-agent review

## Description

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
