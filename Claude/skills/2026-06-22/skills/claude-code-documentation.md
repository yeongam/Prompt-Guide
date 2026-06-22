---
name: Claude Code Documentation
slug: claude-code-documentation
cmd: /init, /team-onboarding
version: 2.1.185
trigger: Use when user asks to generate, update, or maintain project documentation, READMEs, or onboarding guides.
---

Generate and maintain project documentation anchored to actual codebase state.

**Procedure:**
1. Read existing docs to avoid duplication
2. Verify claims against code (don't document phantom features)
3. Keep docs colocated with the code they describe
4. Use imperative mood for instructions; present tense for descriptions
5. Update changelog or version history when modifying existing docs

**For CLAUDE.md:** architecture, commands, conventions only — no tutorials.
**For READMEs:** installation, quickstart, API reference, contributing.
**For onboarding:** `/team-onboarding` generates from local Claude Code usage history.

**Token policy:** Write to file; confirm with one-line summary only.
