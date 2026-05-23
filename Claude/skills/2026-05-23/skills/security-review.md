# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks for security audit of current branch changes

## Procedure

1. Enumerate changed files in current branch diff.
2. Apply OWASP Top 10 checks per change.
3. Check for injection, XSS, auth bypass, sensitive data exposure.
4. Output risk-ranked findings with remediation hints.

## Output

Risk-ranked security findings with OWASP category tags.

## Token Policy

- Report only actionable findings.
- Skip informational notes unless --verbose flag.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.