# UltraPlan

- Slug: `ultraplan`
- Cmd: `/ultraplan`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants cloud environment for complex planning

## Procedure

1. Parse task scope.
2. Create cloud worktrees.
3. Assign subtasks to agents.
4. Synthesize plan.

## Output

Planning environment created with task breakdown.

## Token Policy

- Return final plan only.
- Omit agent coordination logs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
