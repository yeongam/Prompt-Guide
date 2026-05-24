# Ultra Plan

- Slug: `ultraplan`
- Cmd: `/ultraplan`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: cloud multi-agent planning, complex planning tasks

## Procedure

1. Analyze task scope.
2. Spawn cloud worktrees per sub-task.
3. Aggregate and present unified plan.

## Output

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
