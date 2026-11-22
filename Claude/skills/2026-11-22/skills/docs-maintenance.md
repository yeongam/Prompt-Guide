---
name: docs-maintenance
description: Create, trim and audit CLAUDE.md, AGENTS.md, skills and command docs. Use for project-instruction or skill documentation work.
---
Cmds: `/init` (create CLAUDE.md) · `/doctor prompt-audit` (old-model prompt patterns) · `/skill-doctor` (unused skills + cost) · `/reload-skills`
1. Instructions: CLAUDE.md; AGENTS.md per `instructionFiles` (default: only when no CLAUDE.md). Keep one source.
2. Trim: cut anything derivable from code (tree, deps, obvious commands). Keep conventions, gotchas, test/lint cmds.
3. Skill file: frontmatter `name` + one-line `description` (when to use / not use); body = steps + output, ≤15 lines. Frontmatter `model` stays on the skill turn (subagents/compaction keep session model unless `context: fork`).
4. Audit: remove ALL-CAPS pressure, redundant examples, stale model ids, duplicated rules.
Output: changed files + token delta estimate.
