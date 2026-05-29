# Bugfix

- Slug: `bugfix`
- Command: `/bugfix`
- Source: https://github.com/anthropics/claude-code
- Trigger: user reports a specific reproducible bug

## Description

Failing repro first, root-cause, minimal fix, regression test, PR

## Procedure

1. Write failing repro test.
2. Trace root cause.
3. Apply minimal fix.
4. Convert repro to regression test.
5. Open PR.

## Output

Fix + regression test + PR.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
