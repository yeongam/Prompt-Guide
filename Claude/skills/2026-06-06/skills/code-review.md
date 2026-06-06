---
slug: code-review
cmd: /code-review [effort] [--comment] [--fix]
added: v2.1.147
replaces: /simplify
---
trigger: Review current diff for correctness bugs, reuse, and efficiency.

effort: low/medium=high-confidence findings only; high/max=broader coverage
--comment: post findings as inline GitHub PR review comments
--fix: apply findings directly to the working tree
