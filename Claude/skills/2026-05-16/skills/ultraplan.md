# ultraplan

- Cmd: `/ultraplan`
- Trigger: user wants cloud environment for complex planning
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Upstream version: 2.1.142

## Description

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- Return only decision-critical instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
