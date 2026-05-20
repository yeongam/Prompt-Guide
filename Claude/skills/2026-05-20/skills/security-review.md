# Security Review

- Slug: `security-review`
- Cmd: `/security-review`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks security audit of current branch changes

## Procedure

1. Diff current branch.
2. Map findings to OWASP Top 10.
3. Rank by severity.
4. Suggest minimal fixes.

## Output

Risk-ranked security findings with remediation steps.

## Token Policy

- Skip low-risk items unless pattern is widespread.
- Cite OWASP reference codes.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
