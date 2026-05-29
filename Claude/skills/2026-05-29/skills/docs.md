# Docs

- Slug: `docs`
- Command: `/docs`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants documentation written or updated

## Description

Generate/update docs; verify examples and links; open PR

## Procedure

1. Find relevant code and existing doc patterns.
2. Draft outline for target audience.
3. Write content; verify examples; check links.
4. Open PR.

## Output

Documentation PR.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
