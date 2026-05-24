# Power Up

- Slug: `powerup`
- Cmd: `/powerup`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: feature demos, learn Claude Code features

## Procedure

1. Present feature menu.
2. Run selected demo.
3. Return actionable next steps.

## Output

Interactive animated feature demos with lessons

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
