# Verify

- Slug: `verify`
- Command: `/verify`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user wants a specific claim, fix, or finding independently checked

## Procedure

1. Restate the claim to verify.
2. Check it against the actual code/state, not prior assumptions.
3. Report CONFIRMED or REFUTED with the concrete evidence.

## Output

A confirm/refute verdict with supporting evidence.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

No longer auto-invoked; run explicitly with /verify when a claim or fix needs independent confirmation.
