---
name: git-commit
description: Commit current changes in one step. Use when asked to commit.
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
---
Run `git status`, `git diff HEAD`, `git log --oneline -10` in one batch; match message style.
Stage + create one commit in a single response. No other text.
