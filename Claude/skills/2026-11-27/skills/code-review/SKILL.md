---
name: code-review
description: Review a diff or PR for high-signal bugs and CLAUDE.md violations; optionally simplify changed code. Use on "review", "PR review", "check my diff".
---
# Code Review
Src: claude-plugins-official/{code-review,pr-review-toolkit,code-simplifier}@0fbfda5a91f4
Prefer built-in `/code-review [level] [PR#] [--comment|--fix]` when present; this is the fallback.
1. Skip if PR closed/draft/trivial or already reviewed.
2. Collect CLAUDE.md paths (root + dirs of changed files) and a 3-line change summary.
3. Parallel reviewers on the diff only: A) CLAUDE.md compliance (quote rule), B) bugs (compile/logic), C) optional aspect: tests|comments|errors|types.
4. Validate each finding with an independent check; drop unconfirmed.
5. Output `file:line — issue — why`, or "No issues found."; post inline only with `--comment`, one per issue.
Do NOT flag: style, pre-existing, linter-catchable, input-dependent, silenced issues.
Simplify mode: refine only recently changed code; keep behavior identical.
