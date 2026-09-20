# Claude Directory Rules

These rules are fixed for all work under `Prompt-Guide/Claude`.

- Only edit files inside `Claude/` unless the user explicitly expands the scope.
- Keep generated skills under `Claude/skills/YYYY-MM-DD/skills/`.
- Use the official `anthropics/claude-code` GitHub repository as the source of truth for skill updates.
- Keep skill files compact, executable, and token-efficient.
- Remove duplicate prompts, repeated explanations, and inefficient invocation patterns.
- Preserve existing skill behavior before adding new skills.
- Check compatibility before integrating new skills.
- Write changelogs to `Claude/Changelogs/YYYY-MM-DD.txt`.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes for skills.
- Automation must run without interactive prompts or permission popups.
- `Claude/skills/SKILLS_CATALOG.yaml` stays as the compact single-file reference (skills, hooks, settings, env vars, models); dated snapshots under `Claude/skills/YYYY-MM-DD/skills/` hold expanded per-skill cards with source commit provenance.
- Do not modify GPT/ or Gemini/ directories from this routine.
