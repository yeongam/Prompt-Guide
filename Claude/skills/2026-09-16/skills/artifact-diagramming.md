# Artifact Diagramming

- Slug: `artifact-diagramming`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: a diagram would clarify an artifact's mechanism

## Procedure

1. Draw the real mechanism, not decoration.
2. Use inline-SVG mechanics that stay legible in both themes.

## Output

A legible inline-SVG diagram inside the artifact.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
