# ultraplan

- Cmd: `/ultraplan`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants cloud environment for complex planning

## Description

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
