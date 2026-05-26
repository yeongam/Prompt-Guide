# Security Review

- Slug: `security-review`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user asks security audit of current branch changes

## Procedure

1. Diff current branch vs base.
2. Check OWASP top 10: injection, XSS, CSRF, auth, secrets.
3. Rank findings by severity (critical/high/medium/low).
4. Provide fix snippet for each finding.

## Output

Risk-ranked security findings with remediation.

## Token Policy

- Only report findings with clear impact.
- Omit informational notes unless critical.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
