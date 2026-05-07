# Ultraplan (Cloud Planning)

- Slug   : `ultraplan`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user wants cloud environment for complex multi-step planning

## Procedure

1. Run /ultraplan.
2. Auto-create cloud worktrees.
3. Execute parallel planning agents.

## Output

Multi-agent plan with actionable steps.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
