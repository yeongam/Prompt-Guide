---
name: code-review
description: Find correctness bugs in a diff, branch, PR or path. Use when asked to review code. Not for style cleanup (use simplify).
---
Cmd: `/code-review [low|medium|high|xhigh|max] [target] [--comment] [--fix] [--max-findings n|all]`
1. Scope: diff (default) | PR# | branch | path. Read only changed hunks + direct callers.
2. Level: low = few high-confidence; high+ = more, some uncertain. `max` only if explicitly asked.
3. Check: logic, edge cases, error paths, concurrency, security, broken CLAUDE.md rules.
4. Verify each finding with a concrete failing input before reporting.
Output: findings most-severe first → `file:line | defect | failing scenario`. None → say so.
`--comment` posts inline PR comments; `--fix` applies fixes after review.
