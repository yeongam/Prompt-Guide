---
name: hooks-config
description: Add hooks, permissions, env in settings.json. Use for "whenever X", "allow Y", "block Z".
---
1. Pick event from catalog.yaml `hooks`; block = exit 2 or `{"decision":"block","reason":"..."}`.
2. Scope: `.claude/settings.json` (project) or `~/.claude/settings.json` (user); add `if` for conditional.
3. Fewer prompts: `/fewer-permission-prompts` or `permissions.denyInsteadOfPrompting` for unattended runs.
4. Pattern-based generation: `hookify` plugin. Validate: `/status` lists matchers that never match.
