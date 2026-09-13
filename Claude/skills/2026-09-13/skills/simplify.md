# simplify

- Command: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: user asks to clean up or refactor changed code

## Output

Review changed code for reuse/quality/efficiency, then fix issues

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
