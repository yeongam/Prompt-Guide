# simplify

- Cmd: `/simplify`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user asks to clean up or refactor changed code

## Desc

Review changed code for reuse/quality/efficiency, then fix issues

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
