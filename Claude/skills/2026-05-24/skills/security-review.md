# Security Review

- Slug: `security-review`
- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: security audit of current branch changes

## Procedure

1. Isolate changed surfaces.
2. Check OWASP Top 10 and injection vectors.
3. Report findings by severity with remediation.

## Output

OWASP-focused audit of pending diffs; risk-ranked findings

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
