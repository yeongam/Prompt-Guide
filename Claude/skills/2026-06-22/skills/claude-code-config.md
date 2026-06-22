---
name: Claude Code Config
slug: claude-code-config
cmd: /update-config
version: 2.1.185
trigger: Use when user wants automated behaviors, permission rules, hooks, env vars, or any settings.json changes.
---

Configure .claude/settings.json or ~/.claude/settings.json for hooks, permissions, env vars, and automated behaviors.

**Procedure:**
1. Identify target scope: project (.claude/) or user (~/.claude/)
2. Locate or create settings.json
3. Apply change; validate JSON structure
4. Confirm with /config or /doctor

**Common patterns:**
- Permissions: `{"allow": ["Bash(git:*)", "Tool(param:value)"]}` (param-match syntax v2.1.178)
- Hooks: `{"hooks": {"PreToolUse": [{"type": "shell", "command": "..."}]}}`
- Fallback model: `{"fallbackModel": ["claude-sonnet-4-6"]}` (up to 3, v2.1.166)
- Disable bundled skills: `{"disableBundledSkills": true}` (v2.1.170)
- Attribution: `{"attribution": {"sessionUrl": false}}` (v2.1.183)
- Version enforcement: `{"requiredMinimumVersion": "2.1.185"}` (v2.1.163)

**Token policy:** Show only the changed JSON block; not the full file.
