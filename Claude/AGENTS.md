# Claude Directory Rules

These rules are fixed for all work under `Prompt-Guide/Claude`, regardless of which routine run applies them.

- Only edit files inside `Claude/` unless the user explicitly expands the scope.
- Keep generated skills under `Claude/skills/YYYY-MM-DD/skills/`.
- Keep generated hooks under `Claude/hooks/YYYY-MM-DD/hooks/`.
- Use the official Anthropic GitHub repositories (`anthropics/claude-code`, `anthropics/skills`, `anthropics/anthropic-sdk-python`, `anthropics/anthropic-sdk-typescript`, `anthropics/claude-agent-sdk-python`) as the source of truth for skill and hook updates.
- Prioritize coding, programming, and documentation-related skills/hooks found in those repositories.
- Keep skill files compact, executable, and token-efficient.
- Keep hook files compact, non-interactive, and token-efficient.
- Remove duplicate prompts, repeated explanations, and inefficient invocation patterns.
- Preserve existing skill behavior before adding new skills; check compatibility before integrating.
- `Claude/skills/SKILLS_CATALOG.yaml` and `Claude/skills/.version` are a legacy flat catalog kept for backward compatibility; the dated snapshots are the canonical record going forward.
- Write changelogs to `Claude/Changelogs/YYYY-MM-DD.txt`; do not recreate the directory if it already exists.
- Changelogs must list added, modified, deleted, optimized, token-saving, and conflict-resolution changes for skills and hooks.
- Automation must run without interactive prompts or permission popups.
- Do not modify `GPT/` or `Gemini/` directories from Claude routine runs.
