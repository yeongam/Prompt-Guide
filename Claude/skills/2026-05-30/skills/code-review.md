# Code Review

- Slug: `code-review`
- Cmd: `/code-review [--comment] [--fix]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review diff for correctness bugs, reuse, simplification, efficiency

## Flags

| Flag | Effect |
|------|--------|
| (none) | Print findings to stdout |
| `--comment` | Post findings as inline PR comments |
| `--fix` | Apply findings to working tree |
| `--effort low\|medium\|high\|max` | Coverage depth |

## Procedure

1. Diff staged/unstaged changes vs base.
2. Check correctness bugs → reuse → simplification → efficiency.
3. Exclude style nits unless `--effort max`.
4. Apply or comment based on flag.

## Output

Inline findings or applied fixes; summary count at end.

## Token Policy

- Return findings only; no verbose explanations.
- `--fix` mode: show diff, not full file.
- Deduplicate identical patterns.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
