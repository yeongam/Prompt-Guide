# Claude Code Commands

- Slug: `claude-code-commands`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.170`
- Trigger: Use for Claude Code slash commands, CLI flags, and session management.

## Procedure

1. Confirm target command exists in current version.
2. Prefer built-in slash commands over workarounds.
3. Use minimal flags; avoid deprecated options.
4. Verify output matches expected behavior before committing.
5. Link official changelog for version-specific features.

## Output

Concise command reference with version tag and usage note.

## Token Policy

- Return command signature only; omit long examples.
- Link to source repo instead of repeating docs.
- Skip unchanged commands; highlight additions only.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Commands (v2.1.129 → v2.1.170)

### Newly Added
| Cmd | Added | Purpose |
|-----|-------|---------|
| `/cd` | v2.1.169 | Change working directory mid-session without breaking prompt cache |
| `/workflows` | v2.1.154 | View dynamic workflow runs and orchestration |
| `/code-review` | v2.1.147 | Report correctness bugs at chosen effort level (--comment/--fix) |
| `/goal` | v2.1.139 | Set completion condition; Claude works until met |
| `/scroll-speed` | v2.1.139 | Tune mouse wheel scroll speed with live preview |
| `claude agents` | v2.1.139 | Unified list of all Claude Code sessions |
| `claude plugin init` | v2.1.157 | Scaffold new plugin in `.claude/skills` |
| `/plugin list` | v2.1.163 | Display installed plugins with filtering |
| `claude --safe-mode` | v2.1.169 | Start with all customizations disabled for troubleshooting |

### Existing (unchanged)
`/init` `/review` `/security-review` `/simplify` `/ultrareview` `/ultraplan`
`/team-onboarding` `/effort` `/powerup` `/tui` `/focus` `/undo` `/usage`
`/theme` `/color` `/loop` `/update-config` `/keybindings-help`
`/fewer-permission-prompts` `/session-start-hook` `/claude-api`
