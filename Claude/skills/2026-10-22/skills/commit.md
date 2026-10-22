# commit
Use git status/diff HEAD/branch/log -10. Run all calls in ONE message, no extra text.
- /commit: git add + single commit (match recent message style).
- /commit-push-pr: branch off if on main; one commit; push -u origin; open PR (PR only if routine/user requests).
- /clean-gone: `git branch -v`; for each `[gone]` branch (strip `+*`): remove its worktree (`git worktree remove --force`, skip main tree), `git branch -D`. None -> report "no cleanup".
