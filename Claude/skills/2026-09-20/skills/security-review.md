# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `7974a70773fa` (v2.1.278)
- Trigger: user asks for a security audit of pending changes

## Procedure

1. Diff the current branch against its base.
2. Audit for OWASP Top 10 classes (injection, XSS, auth, secrets).
3. Rank findings by exploitability and impact.

## Output

Risk-ranked security findings for the pending diff.

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
