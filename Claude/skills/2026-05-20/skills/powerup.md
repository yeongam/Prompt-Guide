# Powerup Demos

- Slug: `powerup`
- Cmd: `/powerup`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants feature demos or to learn Claude Code features

## Procedure

1. List available demos.
2. Run selected demo.
3. Pause for user confirmation between steps.

## Output

Demo sequence for selected feature.

## Token Policy

- One feature per demo run.
- Skip already-seen demos if history available.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
