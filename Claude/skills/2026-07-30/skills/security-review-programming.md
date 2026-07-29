# Security Review

- Slug: `security-review-programming`
- Command: `/security-review`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User asks for a security audit of pending changes.

## Procedure

1. OWASP-focused audit of the current branch diff.
2. Rank risk by exploitability and blast radius.

## Output

Risk-ranked security findings for pending diffs.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.
