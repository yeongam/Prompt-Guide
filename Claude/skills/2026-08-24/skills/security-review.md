# Security Review

- Slug: `security-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user asks for a security audit of pending branch changes

## Procedure

1. Diff the current branch against its base.
2. Check against OWASP top-10 classes of vulnerability.
3. Rank findings by exploitability and blast radius.

## Output

Risk-ranked list of security findings in the pending diff.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
