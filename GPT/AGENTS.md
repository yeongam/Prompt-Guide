# GPT Directory Rules

These rules are fixed for all work under `Prompt-Guide/GPT`.

- Only edit files inside `GPT/` unless the user explicitly expands the scope.
- Keep generated skills under `GPT/skills/YYYY-MM-DD/skills/`.
- Keep generated hooks under `GPT/hooks/YYYY-MM-DD/hooks/`.
- Use official OpenAI GitHub repositories as the source of truth for skill and hook updates.
- Keep skill files compact, executable, and token-efficient.
- Keep hook files compact, non-interactive, and token-efficient.
- Remove duplicate prompts, repeated explanations, and inefficient invocation patterns.
- Preserve existing skill behavior before adding new skills.
- Check compatibility before integrating new skills or hooks.
- Treat the latest dated GPT skills and hooks as repo-local guidance for Codex work.
- Do not assume remote GitHub Actions can change the live local Codex runtime.
- Write changelogs to `GPT/Changelogs/YYYY-MM-DD.txt`.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes for skills and hooks.
- Automation must run without interactive prompts or permission popups.
