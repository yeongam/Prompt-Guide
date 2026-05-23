# Code Review

- Slug: `code-review`
- Command: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants code review at a specific effort level

## Procedure

1. Accept effort level: low/medium (high-confidence only) or high/max (broad coverage).
2. Review current diff for correctness bugs.
3. Pass --comment to post findings as inline PR comments.

## Output

Correctness-focused findings at requested effort level.

## Token Policy

- Scale output verbosity to effort level.
- Low/medium: top 5 findings max.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.