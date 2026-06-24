# Security Programming

- Slug: `security-programming`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187`
- Trigger: user asks security audit, OWASP check, or vulnerability review of current changes

## Procedure

1. Check official source alignment first.
2. Focus on OWASP Top 10 and injection risks.
3. Review auth, input validation, and data exposure.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

OWASP-focused risk-ranked audit of pending diffs.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical security findings.
- Link to CVE/OWASP docs instead of copying descriptions.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
