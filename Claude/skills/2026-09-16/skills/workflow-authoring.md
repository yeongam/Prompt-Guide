# Workflow Authoring

- Slug: `workflow-authoring`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: authoring a Workflow tool script the user already opted into

## Procedure

1. Split out of the Workflow tool description to cut its footprint from ~5.7k to ~1k tokens.
2. Covers script API, gotchas, resume, and quality patterns.

## Output

A workflow script following the documented API and patterns.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
