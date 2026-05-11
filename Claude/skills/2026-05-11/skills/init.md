# init

- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to initialize or document codebase

## Description

Generate CLAUDE.md with codebase architecture, conventions, commands

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
