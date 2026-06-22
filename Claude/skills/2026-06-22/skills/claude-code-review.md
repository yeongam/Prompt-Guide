---
name: Claude Code Review
slug: claude-code-review
cmd: /review [effort]
version: 2.1.185
trigger: Use when user asks to review a PR, branch diff, or code change for correctness and quality.
---

Multi-pass diff review: correctness bugs, simplification, security, test coverage.

**Procedure:**
1. Read full diff (not just summary)
2. Check logic correctness and edge cases
3. Flag security issues (OWASP top 10)
4. Identify dead code and simplification opportunities
5. Verify test coverage for changed paths

**Effort levels:** low (high-confidence only) | medium (default) | high/max (broader coverage)

**Output:** Ranked findings with file:line references. Use `--comment` to post inline PR comments, `--fix` to apply.

**Token policy:** Report findings only; skip boilerplate analysis text.
