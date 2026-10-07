---
name: git-clean-gone
description: Delete local branches whose remote is gone, plus their worktrees.
---
1. `git branch -v` (`+` = worktree), `git worktree list`.
2. For each `[gone]` branch: `git worktree remove --force <path>` (skip main tree), then `git branch -D <branch>`.
3. Report removed items; if none, say no cleanup needed.
