# Ultra Review

- Slug: `ultrareview`
- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: multi-agent cloud review, ultrareview keyword

## Procedure

1. Launch parallel review agents.
2. Aggregate findings across agents.
3. Output ranked consolidated review.

## Output

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

**Note:** Billed; requires git repo; no GitHub remote needed for local mode
