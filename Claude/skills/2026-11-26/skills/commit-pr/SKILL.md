---
name: commit-pr
description: Commit, push, open PR. Use when asked to commit or create a pull request.
---
1. `git status` + `git diff --stat`; never stage secrets (.env, credentials).
2. Message: imperative subject <=72 chars, body = why.
3. Push `-u origin <branch>`; PR only when explicitly asked; mirror repo PR template.
Plugin equivalent: `commit-commands`.
