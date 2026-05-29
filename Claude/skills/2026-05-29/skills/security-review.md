# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks security audit of current branch changes

## Description

OWASP-focused audit of pending diffs; risk-ranked findings

## Procedure

1. Diff current branch vs base.
2. Map changes to OWASP Top 10.
3. Rank: Critical > High > Medium > Low.

## Output

Severity-ranked findings with remediation hints.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
