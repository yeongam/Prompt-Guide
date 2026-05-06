# GPT Directory Rules

These rules are fixed for all work under `Prompt-Guide/GPT`.

- Only edit files inside `GPT/` unless the user explicitly expands the scope.
- Keep generated skills under `GPT/skills/YYYY-MM-DD/skills/`.
- Use official OpenAI GitHub repositories as the source of truth for updates.
- Keep skill files compact, executable, and token-efficient.
- Remove duplicate prompts, repeated explanations, and inefficient invocation patterns.
- Preserve existing skill behavior before adding new skills.
- Check compatibility before integrating new skills.
- Write changelogs to `GPT/Changelogs/YYYY-MM-DD.txt`.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes.
- Automation must run without interactive prompts or permission popups.
