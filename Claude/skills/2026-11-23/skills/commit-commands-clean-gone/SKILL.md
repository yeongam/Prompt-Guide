---
name: commit-commands-clean-gone
description: "Cleans up all git branches marked as [gone] (branches that have been deleted on the remote but still exist locally), including removing associated worktrees."
---
`command` · plugin `commit-commands` · `/commit-commands:clean_gone`
Src: https://github.com/anthropics/claude-plugins-official/blob/65adb96f26de/plugins/commit-commands/commands/clean_gone.md
Outline (full text at Src):
1. Your Task
2. Commands to Execute
3. First, list branches to identify any with [gone] status
4. Next, identify worktrees that need to be removed for [gone] branches
5. Finally, remove worktrees and delete [gone] branches (handles both regular and…
