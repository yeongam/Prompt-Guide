# /reload-skills — Reload Skill Directories

- Slug: `reload-skills`
- Cmd: `/reload-skills`
- Added: v2.1.152
- Trigger: User added or edited skill files and wants them active without restarting Claude Code.

## Procedure

1. Run `/reload-skills`.
2. All `.claude/skills/` directories are rescanned.
3. New/changed skills become available immediately.

## Output

List of loaded skills and any conflicts resolved with `<dir>:<name>` syntax.

## Token Policy

- One-line confirmation; list only new/changed entries.
