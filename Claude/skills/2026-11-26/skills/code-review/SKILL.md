---
name: code-review
description: Review diffs/PRs for bugs, cleanups, security. Use when asked to review, audit, or clean up changed code.
---
1. Bugs: `/code-review <low|medium|high|xhigh>` (diff) or `/code-review <level> <pr#>`; `--comment` posts inline, `--fix` applies.
2. Cleanups only: `/simplify`. Security: `/security-review`.
3. Deep/billed: `/ultrareview [pr#]` — only on explicit request.
4. Plugin route: `code-review` or `pr-review-toolkit` (claude-plugins-official).
Output: findings ranked by severity, file:line, one-line fix each. No praise, no restated diff.
