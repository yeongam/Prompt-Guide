# pr-review
## /code-review-pr [--comment] <PR>
1. haiku: stop if PR closed/draft/trivial/already reviewed by Claude.
2. haiku: list relevant CLAUDE.md paths. sonnet: PR summary.
3. Parallel: 2x sonnet CLAUDE.md compliance; 2x opus bugs (diff-only; introduced code).
4. Validate each bug/violation with a subagent; drop unvalidated.
Flag only: compile/parse errors, definite wrong results, quotable CLAUDE.md violations. Skip: style, pre-existing, linter-catchable, input-dependent, nits.
Output list, or "No issues found. Checked for bugs and CLAUDE.md compliance." Post only with --comment: one inline comment/issue; committable suggestion only if it fully fixes; links use full SHA + #Lstart-Lend.
Tools: no exploratory calls; every call needs a purpose.
## /review-pr [aspects]
Aspects (default all applicable): comments, tests, errors, types, code, simplify. One specialist agent each on changed files; report critical/important/suggestions + strengths.
