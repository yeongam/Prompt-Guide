# Autofix PR

- Slug: `autofix-pr`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.161` (CHANGELOG.md)
- Trigger: User wants CI failures or reviewer feedback on an open PR fixed automatically.

## Procedure

1. Diagnose the failing check or review comment.
2. Push a minimal fix scoped to that failure.
3. Report progress via the background task's progress count.

## Output

Green CI / addressed review comment on the target PR.

## Token Policy

- Runs as a background cloud session; does not block the local session.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Requires a git repo; not the default branch (worktree fix in v2.1.161).

## Source Summary

> Fixed `/autofix-pr` reporting "cannot run on the default branch" when the session is inside a git worktree or another repository.
