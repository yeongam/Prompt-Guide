# Security Review

- Slug: `security-review`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: User asks for a security audit of the pending changes on the current branch.

## Procedure

1. Scope to the current branch's pending diff.
2. Audit against OWASP-style categories (injection, XSS, auth, secrets, deserialization, etc.).
3. Rank findings by risk.

## Output

Risk-ranked security findings for the pending diff.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml` instead of duplicating it here.

## Compatibility

- Do not overwrite existing dated skill snapshots; integrate only if content changed.

## Source Summary

Official Claude Code skill: OWASP-focused audit of pending diffs, outputs risk-ranked findings. No changelog-visible behavior change between v2.1.129 and v2.1.241.
