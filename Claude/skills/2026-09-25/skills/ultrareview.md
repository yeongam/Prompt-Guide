# ultrareview

- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user says "ultrareview" or wants multi-agent review

## Desc

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
