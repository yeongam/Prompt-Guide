# Security Review

- Slug   : `security-review`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user asks security audit of current branch changes

## Procedure

1. Diff current branch.
2. Map findings to OWASP Top 10.
3. Rank by severity.
4. Output fix snippets for critical/high only.

## Output

OWASP-mapped findings with severity and fix snippet.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
