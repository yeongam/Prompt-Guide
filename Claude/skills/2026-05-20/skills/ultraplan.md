# ultraplan

- Slug: `ultraplan`
- Command: `/ultraplan`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants cloud environment for complex planning

## Description

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
