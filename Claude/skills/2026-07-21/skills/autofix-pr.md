# Autofix PR

- Slug: `autofix-pr`
- Command: `/autofix-pr`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user wants CI failures or review comments on an open PR fixed automatically

## Procedure

1. Read failing checks / review comments on the target PR.
2. Diagnose and push a fix commit.
3. Re-check CI status after pushing.

## Output

A fix pushed to the PR branch, or a diagnosis if out of scope.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Works from a git worktree or another repository without the earlier 'cannot run on the default branch' false rejection.
