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
- Treat the latest dated Claude skills and hooks as repo-local guidance for Claude Code work.
- Do not assume remote GitHub Actions can change the live local Claude Code runtime.
- Write changelogs to `Claude/Changelogs/YYYY-MM-DD.txt`.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes for skills and hooks.
- Automation runs non-interactively via the pre-approved allowlist in `.claude/settings.json`; it does not grant standing authority to skip confirmation for anything outside this directory's routine sync.
