# security-review

- Slug: `security-review`
- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks for security audit of current branch changes.

## Procedure

1. Diff current branch against base.
2. Check OWASP Top 10: injection, XSS, auth, exposure.
3. Output risk-ranked findings with remediation hints.

## Output

Risk-ranked findings; HIGH items block merge recommendation.

## Token Policy

- Diff-scoped; one finding per unique issue.

## Compatibility

- Read-only; no auto-fix. Pair with /review for full coverage.
