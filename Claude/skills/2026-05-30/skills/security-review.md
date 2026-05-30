# Security Review

- Slug: `security-review`
- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks security audit of current branch changes

## Procedure

1. Diff current branch vs base.
2. Check OWASP Top 10: injection, auth, XSS, IDOR, SSRF, secrets in code.
3. Check dependency additions for known CVEs.
4. Risk-rank each finding.
5. Suggest minimal fix per finding.

## Output

Risk-ranked list: CRITICAL / HIGH / MEDIUM. No LOW unless asked.

## Token Policy

- Return ranked list only.
- Link OWASP reference per finding (no inline quotes).
- One-line fix suggestion per finding.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
