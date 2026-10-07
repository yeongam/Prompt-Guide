---
name: pr-review-highsignal
description: High-signal PR review (bugs + CLAUDE.md compliance). Complements built-in review/code-review; use for `--comment` posting flows.
---
1. Skip if PR closed/draft/trivial/automated or already reviewed by Claude (Claude-authored PRs still reviewed).
2. Collect root + touched-dir CLAUDE.md paths; summarize PR.
3. Parallel reviewers: 2× CLAUDE.md compliance, 2× bug (diff-only, no extra context).
4. Validate each finding with a separate agent; drop unvalidated.
Flag only: compile/parse errors, definite wrong results, quotable CLAUDE.md violations.
Ignore: style, input-dependent issues, pre-existing, linter-catchable, silenced-in-code, speculative.
5. Output list or "No issues found. Checked for bugs and CLAUDE.md compliance."
6. Only with `--comment`: post one inline comment per issue (link full-SHA permalink `#L{s}-L{e}` with 1 line context; suggestion block only if it fully fixes). No issues → summary comment.
Use `gh`, not web fetch.
