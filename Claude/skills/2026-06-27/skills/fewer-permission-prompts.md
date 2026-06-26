# /fewer-permission-prompts — fewer-permission-prompts

- Category : `config`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants fewer permission dialogs.

**Action** : Scan transcripts → add bash/MCP allowlist to .claude/settings.json.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.
