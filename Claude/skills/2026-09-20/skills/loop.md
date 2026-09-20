# Loop

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `7974a70773fa` (v2.1.278)
- Trigger: user wants a recurring task ("check every 5m", "keep running X")

## Procedure

1. Parse the interval and target prompt/command.
2. Schedule repeated firing at that interval, self-pacing if omitted.
3. Stop cleanly when the user ends the loop.

## Output

Recurring execution of the given prompt/command at the set interval.

## Token Policy

- Avoid repeated background context across turns.
- Return only decision-critical instructions or code.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve GPT/Gemini directory behavior; do not modify them.

## Source Summary

2.1.278 - Changed auto mode for Claude API and Enterprise users, and on Bedrock, Vertex,
Foundry and gateways, to default to the server-side classifier, which does not charge
for classifier overhead (`CLAUDE_CODE_AUTO_MODE_SERVER=0` opts out on Bedrock, Vertex,
Foundry and gateways); warns on billed fallback. See
https://code.claude.com/docs/en/auto-mode-classifier-billing - Added an `Auto mode
server` row to `/stat.
