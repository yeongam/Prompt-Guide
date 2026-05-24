# Code Review

- Slug: `code-review`
- Cmd: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: review diff for bugs, code correctness review

## Procedure

1. Read current diff.
2. Check for correctness bugs at specified effort.
3. Output findings or post inline PR comments.

## Output

Review diff at given effort level; --comment posts inline PR comments

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
