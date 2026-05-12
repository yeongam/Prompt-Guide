# commit-commands
source: anthropics/claude-code/plugins/commit-commands
updated: 2026-05-12

## Purpose
Automates git commit, push, and PR creation workflows.

## Commands
/commit            – Stage + commit with auto-generated message matching repo style
/commit-push-pr    – Full workflow: branch → commit → push → PR with description
/clean_gone        – Remove local branches deleted from remote (handles worktrees)

## Requirements
- /commit-push-pr requires GitHub CLI (gh) authenticated
