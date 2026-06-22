---
name: Claude Code Init
slug: claude-code-init
cmd: /init
version: 2.1.185
trigger: Use when user asks to initialize, document, or scaffold a new codebase for Claude Code.
---

Generate CLAUDE.md with codebase architecture, conventions, key commands, and project context.

**Procedure:**
1. Scan repo structure and identify tech stack
2. Extract key commands (build, test, lint, run)
3. Document architecture decisions and conventions
4. Write concise CLAUDE.md at repo root

**Output:** CLAUDE.md ready for session context loading.

**Token policy:** Write to file; do not repeat full content in chat.
