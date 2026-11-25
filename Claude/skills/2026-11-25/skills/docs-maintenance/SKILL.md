---
name: docs-maintenance
description: Create/trim CLAUDE.md, AGENTS.md, skills and READMEs. Use for project docs or prompt files.
---
1. New project: `/init`. Existing: `/doctor prompt-audit` flags outdated prompting; `/doctor` proposes CLAUDE.md trims.
2. Keep only non-derivable facts: commands, conventions, gotchas. Cut what code already shows.
3. Skills: frontmatter `name` + one-line `description` with trigger; body <=15 lines.
4. Prune with `/skill-doctor` (unused skills + context cost).
