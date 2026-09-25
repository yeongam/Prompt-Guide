# effort

- Cmd: `/effort`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user wants to adjust effort/quality level

## Desc

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
