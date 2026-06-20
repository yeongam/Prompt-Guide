# Config Management

**Trigger:** Inline configuration changes, settings.json edits, env var setup
**Added:** v2.1.180

## Procedure
1. Use `/config key=value` for single inline key changes
2. Use `/update-config` for hooks, permissions, env var blocks
3. Verify with `/doctor` after applying
4. Prefer project `settings.json` over user-level for team repos
5. Document non-obvious config in CLAUDE.md

## Token Policy
- Return only the changed key-value pair
- Skip unchanged config blocks
- Link to settings reference instead of repeating docs

## Key Settings (v2.1.183)
| Key | Type | Purpose |
|-----|------|---------|
| `attribution.sessionUrl` | bool | Omit claude.ai session link from commits/PRs |
| `skillOverrides` | enum | Control skill visibility to model |
| `autoScrollEnabled` | bool | Disable TUI auto-scroll |
| `disableSkillShellExecution` | bool | Block inline shell in skills |

## Skill Commands
- `/config [key=value]` — inline config setter (NEW v2.1.180)
- `/update-config` — full settings.json configurator
- `/doctor` — verify config is applied correctly
