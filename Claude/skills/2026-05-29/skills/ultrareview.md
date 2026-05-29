# Ultra Review

- Slug: `ultrareview`
- Command: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user says 'ultrareview' or wants multi-agent review

## Description

Parallel multi-agent cloud code review; local or GitHub PR

## Procedure

1. Spawn parallel review agents.
2. Each agent focuses on a different concern.
3. Merge findings, deduplicate.

## Output

Merged multi-agent review findings.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Notes

Billed; requires git repo.
