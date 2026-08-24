# Skill Creator

- Slug: `skill-creator`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user wants to create, edit, or optimize a skill

## Procedure

1. Scaffold or edit the skill's SKILL.md and supporting files.
2. Tighten the description for accurate triggering.
3. Optionally run evals to benchmark performance.

## Output

A new or improved skill definition, optionally with eval results.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
