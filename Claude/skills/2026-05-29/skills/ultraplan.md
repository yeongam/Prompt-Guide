# Ultra Plan

- Slug: `ultraplan`
- Command: `/ultraplan`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants cloud environment for complex planning

## Description

Auto-create cloud worktrees for multi-agent planning

## Procedure

1. Parse task scope.
2. Create cloud worktrees/environments.
3. Run multi-agent planning.

## Output

Multi-agent plan output.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
