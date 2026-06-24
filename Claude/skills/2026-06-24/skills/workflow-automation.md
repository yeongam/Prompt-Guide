# Workflow Automation

- Slug: `workflow-automation`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187`
- Trigger: user wants recurring tasks, hooks, cron jobs, or automated pipeline setup

## Procedure

1. Check official source alignment first.
2. Prefer smallest working automation structure.
3. Use hooks for event-driven triggers; cron for time-based.
4. Keep automation scripts short and single-purpose.
5. Verify automation runs without user input.

## Output

Lean automation design with hook/cron implementation.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical automation config.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
