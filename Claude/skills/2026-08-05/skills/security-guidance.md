# security-guidance

- Slug: `security-guidance`
- Category: security
- Source: https://github.com/anthropics/claude-code/tree/main/plugins/security-guidance
- Source repo version: `2.1.221`
- Trigger: Use for security work matching: Security reminder hook that warns about potential security issues when editing files, including command injection, XSS, and unsafe code pat.

## Procedure

1. Confirm the task matches this plugin's stated purpose before invoking it.
2. Prefer the plugin's built-in agents/commands over ad hoc reimplementation.
3. Keep generated output scoped to the task at hand.
4. Verify results with the narrowest relevant check.

## Output

Security reminder hook that warns about potential security issues when editing files, including command injection, XSS, and unsafe code patterns

## Token Policy

- Do not copy upstream plugin documentation verbatim.
- Return only decision-critical guidance.
- Link to source instead of repeating long descriptions.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Security reminder hook that warns about potential security issues when editing files, including command injection, XSS, and unsafe code patterns
