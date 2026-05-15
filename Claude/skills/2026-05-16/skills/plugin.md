# plugin

- Cmd: `/plugin`
- Trigger: user wants to install or manage Claude Code plugins
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Install, update, or remove Claude Code plugins and extensions

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
