# team-onboarding

- Cmd: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants teammate ramp-up guide

## Description

Generate onboarding guide from local Claude Code usage history/data

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
