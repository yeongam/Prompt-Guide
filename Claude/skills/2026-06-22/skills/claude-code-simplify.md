---
name: Claude Code Simplify
slug: claude-code-simplify
cmd: /simplify
version: 2.1.185
trigger: Use when user asks to clean up, refactor, or simplify changed code for quality and efficiency.
---

Review changed code for reuse, simplification, efficiency, and altitude cleanups; apply fixes.

**Procedure:**
1. Identify duplicate logic or abstraction candidates
2. Remove dead code and unnecessary wrappers
3. Inline trivial helpers; extract non-trivial repeated patterns
4. Prefer stdlib/framework idioms over custom implementations
5. Apply fixes directly; do not generate a report only

**Scope:** Quality only — bug hunting belongs to /review.

**Token policy:** Apply edits silently; summarize in one line per file changed.
