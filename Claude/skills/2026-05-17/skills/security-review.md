# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User asks for security audit of current branch changes

## Procedure

1. Run diff against OWASP Top 10 checklist.
2. Flag injection, auth, secrets, and dependency issues.
3. Rank findings by exploitability and impact.
4. Provide minimal remediation per finding.

## Output

OWASP-focused findings ranked by risk

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
