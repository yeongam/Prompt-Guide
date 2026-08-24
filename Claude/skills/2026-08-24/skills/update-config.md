# Update Config

- Slug: `update-config`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user wants automated behaviors, permissions, env vars, or hooks configured

## Procedure

1. Edit settings.json / settings.local.json rather than relying on memory.
2. Wire hooks for behaviors that must fire automatically on lifecycle events.

## Output

Updated settings.json implementing the requested automated behavior.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
