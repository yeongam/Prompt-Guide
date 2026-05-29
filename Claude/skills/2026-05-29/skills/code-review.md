# Code Review

- Slug: `code-review`
- Command: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants code reviewed for bugs or cleanups

## Description

Review diff: correctness, reuse, simplification, efficiency

## Procedure

1. Read diff at requested effort level.
2. Flag correctness bugs first.
3. Then reuse/simplification/efficiency issues.
4. Post inline comments if --comment; apply if --fix.

## Output

Findings list or inline PR comments.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
