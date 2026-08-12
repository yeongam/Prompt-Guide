# Claude Directory Rules

These rules are fixed for all work under `Prompt-Guide/Claude`.

- Only edit files inside `Claude/` unless the user explicitly expands the scope.
- Keep generated skills under `Claude/skills/YYYY-MM-DD/skills/`.
- Keep generated hooks under `Claude/hooks/YYYY-MM-DD/hooks/`.
- Use official Anthropic GitHub repositories as the source of truth for skill and hook updates.
- Keep skill files compact, executable, and token-efficient.
- Keep hook files compact, non-interactive, and token-efficient.
- Remove duplicate prompts, repeated explanations, and inefficient invocation patterns.
- Preserve existing skill behavior before adding new skills.
- Check compatibility before integrating new skills or hooks.
- `skills/.version` and `skills/SKILLS_CATALOG.yaml` are a separate, pre-existing catalog
  maintained by `scripts/update_skills.py` at the repo root — do not remove them; only
  update their `version`/`updated` fields when the upstream CHANGELOG version changes.
- Write changelogs to `Claude/Changelogs/YYYY-MM-DD.txt`.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes for skills and hooks.
- Automation must run without interactive prompts, since it also runs unattended in GitHub Actions.
- Never fabricate source commits, version numbers, or feature names; only record what was actually fetched from the official source.
