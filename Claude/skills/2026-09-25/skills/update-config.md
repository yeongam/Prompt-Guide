# update-config

- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Desc

Configure settings.json; handles hooks, permissions, env vars

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
