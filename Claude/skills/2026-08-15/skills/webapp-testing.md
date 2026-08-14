# webapp-testing

- Slug: `webapp-testing`
- Source: https://github.com/anthropics/skills/tree/main/skills/webapp-testing
- Source commit: `ref:main`
- Trigger: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.

## Output

Compact, repeatable instructions for the task the skill covers.

## Token Policy

- Reference the upstream SKILL.md instead of copying its full body.
- Keep the local card to trigger + one-line output + policy notes.
- Load full skill content only when the skill actually fires.

## Compatibility

- Namespaced separately from Claude Code slash-command skills.
- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

# Web Application Testing To test local web applications, write native Python Playwright scripts. **Helper Scripts Available**: - `scripts/with_server.py` - Manages server lifecycle (supports multiple servers) **Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very larg.
