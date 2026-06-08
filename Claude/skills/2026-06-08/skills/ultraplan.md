# ultraplan

- Slug: `ultraplan`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants cloud environment for complex planning

## Procedure

Command: `/ultraplan`

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.