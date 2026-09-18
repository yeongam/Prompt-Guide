# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Audit pending changes on the current branch for OWASP-class issues.

## Procedure

1. Diff the current branch against its base.
2. Flag injection, auth, secrets, and unsafe deserialization risks.
3. Rank by exploitability and blast radius.

## Output

Risk-ranked security findings for the pending diff.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.
