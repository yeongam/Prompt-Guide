---
name: Claude Code CD (Change Directory)
slug: claude-code-cd
cmd: /cd [path]
version: 2.1.170
added: v2.1.170
trigger: Use when user wants to move the active session to a different working directory without losing prompt cache.
---

Move session working directory without breaking prompt cache context.

**Usage:** `/cd /path/to/project` or `/cd ../sibling-dir`

**Behavior:**
- Resets tool working directory to target path
- Preserves conversation history and cached context
- Recalculates CLAUDE.md search path from new root

**Token policy:** Confirm new path in one line only.
