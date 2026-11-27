---
name: claude-md-management
description: Audit, improve, or update CLAUDE.md files; capture session learnings. Use on "audit/update CLAUDE.md", "remember this for the project".
---
# CLAUDE.md Management
Src: claude-plugins-official/{claude-md-management,claude-code-setup}@0fbfda5a91f4
1. Find all CLAUDE.md (root, nested, `.claude/`).
2. Score each: commands, architecture, conventions, gotchas, conciseness, currency.
3. Report: per-file score + top issues (stale commands, duplication, vague rules).
4. Targeted edits only: add verified commands/gotchas; delete stale/duplicate lines.
5. Revise mode: append concise learnings from this session (1 line each).
Keep CLAUDE.md short; it loads every turn — every line costs tokens.
Setup mode: recommend hooks/skills/MCP/subagents fitted to the repo (top 1-2 each).
