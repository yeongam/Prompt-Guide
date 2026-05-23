# Ultra Review

- Slug: `ultrareview`
- Command: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Trigger: User says 'ultrareview' or wants multi-agent parallel review

## Procedure

1. No-arg: bundle local branch, run parallel multi-agent review.
2. With PR#: fetch GitHub PR diff, run parallel agents.
3. Aggregate findings across agents, deduplicate.

## Output

Consolidated multi-agent review report.

## Token Policy

- Deduplicate cross-agent findings before output.
- Billed operation — confirm scope before running.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.