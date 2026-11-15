---
name: commit-push-pr
description: Commit, push, and open a PR in one step. Use when the user asks to commit and open a pull request.
allowed-tools: Bash(git checkout:*), Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
---
<!-- src: anthropics/claude-code .claude/commands/commit-push-pr.md @0cb75ce -->
Context: !`git status --short` | !`git branch --show-current` | !`git diff HEAD --stat`

Do all steps in one response, tool calls only, no extra text:
1. If on default branch → create branch.
2. One commit, clear message.
3. Push branch to origin.
4. `gh pr create`.
