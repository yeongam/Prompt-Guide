# Settings & Hooks Configuration

- Slug: `settings-hooks-config`
- Command: `/update-config`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Automated-behavior requests ("when X", "allow Y", "set Z=val").

## Procedure

1. Edit settings.json for hooks, permissions, or env vars.
2. Prefer narrow permission scopes over broad allowlists.

## Output

settings.json updated with the requested hook/permission/env change.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.
