# PR & Branch Review

- Slug: `pr-review-programming`
- Command: `/review`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User asks to review a PR or branch.

## Procedure

1. Multi-pass check: logic, style, security, tests.
2. Rank findings by severity before reporting.

## Output

Ranked review findings for the diff under review.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.
