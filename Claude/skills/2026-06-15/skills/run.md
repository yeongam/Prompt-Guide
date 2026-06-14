# run

- Cmd: `/run`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.177`
- Trigger: user wants to run or start the app

## Description

Launch and drive project app; screenshots or confirms changes in real app

## Token Policy

- One-line description per skill; no background context in output.
- Reference source version for audit; omit if tokens are critical.
- Link to release notes instead of copying upstream docs.
- Return only decision-critical guidance or commands.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
- Do not modify GPT or other non-Claude directories.
