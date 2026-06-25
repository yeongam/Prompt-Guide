# fewer-permission-prompts

**cmd:** `/fewer-permission-prompts`
**trigger:** user wants fewer permission dialogs
**desc:** Scan transcripts → add bash/MCP allowlist to .claude/settings.json

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.