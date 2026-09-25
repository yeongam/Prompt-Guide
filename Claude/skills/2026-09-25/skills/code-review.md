# code-review

- Cmd: `/code-review`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user asks to review a diff, PR, branch, or path

## Desc

Multi-pass review for correctness bugs plus reuse/simplification/efficiency cleanups

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
