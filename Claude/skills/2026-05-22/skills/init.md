# init

- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user asks to initialize or document codebase

## Description

Generate CLAUDE.md with codebase architecture, conventions, commands

## Token Policy

- One-pass generation; no repeated file reads after initial scan.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.
