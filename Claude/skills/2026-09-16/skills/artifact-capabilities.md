# Artifact Capabilities

- Slug: `artifact-capabilities`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: an artifact needs runtime behavior (live data, saved state, per-viewer memory)

## Procedure

1. Load before declaring `capabilities` or writing `window.claude.*` runtime code.

## Output

An artifact wired to the correct runtime capability contract.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
