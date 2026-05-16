# Ultrareview

- Slug: `ultrareview`
- Command: `/ultrareview [PR#]`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User says 'ultrareview' or wants multi-agent review
- Note: Billed; requires git repo

## Procedure

1. Bundle local branch (no-arg) or fetch GitHub PR.
2. Run parallel agents across review dimensions.
3. Merge findings into ranked report.

## Output

Parallel multi-agent code review report

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
