# web-setup

- Cmd: `/web-setup`
- Trigger: user wants to configure Claude Code for web or remote environment
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Set up Claude Code for web sessions; configure remote execution environment

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
