# code-review

- Slug: `code-review`
- Cmd: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks for code review at specific effort level.

## Procedure

1. Accept effort: low/medium/high/max.
2. Review diff for correctness, reuse, efficiency.
3. --comment posts inline PR comments; --fix applies fixes.

## Output

Findings list with file:line refs; applied fixes if --fix.

## Token Policy

- low/med: high-confidence only. high/max: broader coverage.

## Compatibility

- Distinct from /review (PR-focused).
