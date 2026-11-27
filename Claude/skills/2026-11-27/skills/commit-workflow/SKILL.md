---
name: commit-workflow
description: Create a commit, commit+push+PR, or prune [gone] branches. Use on "commit", "push and open PR", "clean branches".
---
# Commit Workflow
Src: claude-plugins-official/commit-commands@0fbfda5a91f4
Context (one call): `git status`, `git diff HEAD`, `git branch --show-current`, `git log --oneline -10`.
- commit: stage relevant files + single commit; message matches repo log style; no extra text.
- commit-push-pr: branch if on default → commit → `git push -u` → open PR (template headings if present).
- clean-gone: `git fetch -p`; delete local branches marked `[gone]` and their worktrees.
Never commit secrets (.env, credentials). Tool calls only, no narration.
