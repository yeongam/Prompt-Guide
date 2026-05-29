# Autopilot

- Slug: `autopilot`
- Command: `/autopilot`
- Source: https://github.com/anthropics/claude-code
- Trigger: self-contained coding task to complete end-to-end

## Description

Plan, adversarial critique, implement, bug-hunt, open PR

## Procedure

1. Scope problem.
2. Plan with 5-angle adversarial critique.
3. Implement.
4. Bug-hunt + completeness check.
5. Open PR.

## Output

Completed feature + PR link.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
