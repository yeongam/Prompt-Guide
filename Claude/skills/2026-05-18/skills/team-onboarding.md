# team-onboarding

- Cmd: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants teammate ramp-up guide

## Description

Generate onboarding guide from local Claude Code usage history/data

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
