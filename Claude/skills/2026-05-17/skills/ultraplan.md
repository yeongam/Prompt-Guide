# Ultraplan

- Slug: `ultraplan`
- Command: `/ultraplan`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants cloud environment for complex planning

## Procedure

1. Create cloud worktrees for isolated planning.
2. Run parallel planning agents.
3. Present consolidated plan.

## Output

Multi-agent planning result with worktrees

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
