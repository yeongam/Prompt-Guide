# Code Review

- Slug: `code-review`
- Source: anthropics/claude-code CHANGELOG.md (verified fetch, version 2.1.226)
- Trigger: Review the current diff, or a PR number/branch/path target, for correctness bugs and cleanup opportunities.

## Procedure

1. `/review` is now an alias of `/code-review`.
2. No effort level given → reuse the level typed last; `/code-review high` to change it.
3. Runs as a background subagent — review work no longer fills the conversation.
4. `/code-review ultra` for a deep cloud review; `<pr#>` targets a specific PR.
5. Optional flags: `--comment` posts inline PR comments, `--fix` applies findings.

## Output

Risk-ranked findings (correctness bugs first, then reuse/simplification/efficiency).

## Token Policy

- Findings only; no restated diff content.
- Effort level controls finding volume, not verbosity per finding.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
