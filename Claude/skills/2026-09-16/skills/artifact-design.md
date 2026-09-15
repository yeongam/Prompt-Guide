# Artifact Design

- Slug: `artifact-design`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: load before writing any HTML/Markdown artifact

## Procedure

1. Apply design fundamentals before the first line of an artifact.
2. Applies even to skill-instructed Markdown artifacts.

## Output

An artifact that follows the design system's fundamentals.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
