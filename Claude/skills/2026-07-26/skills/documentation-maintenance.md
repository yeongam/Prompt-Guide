# Documentation Maintenance

- Slug: `documentation-maintenance`
- Source: https://github.com/anthropics/claude-code
- Source ref: `CHANGELOG.md` (branch `main`)
- CLI version context: 2.1.220
- Trigger: Use for updating docs, changelogs, and skill catalogs after a Claude Code release.

## Procedure

1. Check the official source file for current behavior before answering.
2. Prefer the smallest working implementation.
3. Use structured APIs/config keys over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command or test.

## Output

Concise doc-update checklist with version traceability.

## Token Policy

- Avoid repeated background context across turns.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.
- Preserve changelog evidence for every generated update.

## Source Summary

# Changelog ## 2.1.220 - Bug fixes and reliability improvements ## 2.1.219 - Added
Claude Opus 5 (`claude-opus-5`), now the default Opus model — 1M context, fast mode at
$10/$50 per Mtok - Added `sandbox.network.strictAllowlist` setting to deny non-
allowlisted hosts for sandboxed commands without prompting - Added `DirectoryAdded` hook
that fires after `/add-dir` or the SDK `register_repo_root` control request regis.
