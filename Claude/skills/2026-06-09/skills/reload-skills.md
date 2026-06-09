# Reload Skills

- Slug: `reload-skills`
- Source: anthropics/claude-code v2.1.169
- Trigger: User wants to apply new or edited skill files without restarting the session.

## Procedure

1. Use `/reload-skills` to re-scan skill directories.
2. Session continues without restart.
3. All newly added or modified .md skill files become immediately available.

## Output

Confirmation of re-scanned skills list.

## Token Policy

- Return only updated skill count or changed skill names.
- No full catalog dump unless requested.

## Compatibility

- Added: v2.1.169
- Safe to use at any point during a session.
