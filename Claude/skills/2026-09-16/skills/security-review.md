# Security Review

- Slug: `security-review`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user asks for a security audit of pending branch changes

## Procedure

1. OWASP-focused audit of the pending diff.
2. Outputs risk-ranked findings.

## Output

Risk-ranked security findings for the current diff.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
