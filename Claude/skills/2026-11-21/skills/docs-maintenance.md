---
name: docs-maintenance
description: Create, trim and audit CLAUDE.md, AGENTS.md, skills and command docs. Use for project-instruction or skill documentation work.
---
Cmds: `/init` (create CLAUDE.md) · `/doctor prompt-audit` (old-model prompt patterns) · `/skill-doctor` (unused skills + cost) · `/reload-skills`
1. Instructions file: CLAUDE.md; AGENTS.md used when CLAUDE.md absent. Keep one source; no duplicate copies.
2. Trim: cut anything derivable from code (tree, deps, obvious commands). Keep conventions, gotchas, test/lint cmds.
3. Skill file: frontmatter `name` + one-line `description` (when to use / not use); body = steps + output, ≤15 lines.
4. Audit: remove ALL-CAPS pressure, redundant examples, stale model ids, duplicated rules.
Output: changed files + token delta estimate.
