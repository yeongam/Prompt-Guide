---
name: git-commit-push-pr
description: Commit, push, open PR in one step. Use only when user asks for a PR.
allowed-tools: Bash(git checkout --branch:*), Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
---
Inspect `git status`/`git diff HEAD`/branch, then in one response: branch if on main → single commit → push origin → `gh pr create`. No other text.
