# /code-review — Code Review

- Slug: `code-review`
- Cmd: `/code-review [--comment] [--fix] [effort]`
- Added: v2.1.152
- Trigger: User asks to review code for bugs, reuse, efficiency; multi-effort support.

## Procedure

1. Diff current branch against base.
2. Run at requested effort level (low/medium/high/max).
3. `--comment`: post findings as inline PR comments.
4. `--fix`: apply findings directly to working tree.

## Output

Risk-ranked findings: correctness bugs → reuse → efficiency → cleanup.

## Token Policy

- Return only decision-critical findings.
- Skip findings below effort threshold.
- One line per finding; group by file.

## Compatibility

- Supersedes `/simplify` for bug-finding; `/simplify` retained for cleanup-only pass.
- Requires git repo with diff-able base branch.
