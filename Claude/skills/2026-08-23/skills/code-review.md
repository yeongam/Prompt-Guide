# Code Review

- Slug: `code-review`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: Review the current diff, PR, branch, or path target for correctness bugs and reuse/simplification/efficiency cleanups.

## Procedure

1. Scope the target: current diff, or a given PR number/branch/path.
2. Run at the requested effort level (low/medium: few high-confidence findings; high→max: broader, may include uncertain findings).
3. Check logic, style, security, and test coverage.
4. Support `--comment` to post inline PR comments, and `--fix` to apply findings to the working tree.
5. Report findings most-severe first via the structured findings tool.

## Output

Risk-ranked findings list; optionally inline PR comments or applied fixes.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml` instead of restating it here.
- Keep this card to trigger + procedure + delta from the previous dated snapshot.

## Compatibility

- `/review` is a legacy alias of `/code-review` since v2.1.227 — do not treat it as a separate skill.
- Runs as a background subagent since v2.1.218; do not assume synchronous completion.
- Do not overwrite existing dated skill snapshots; integrate only if content changed.

## Source Summary

Official Claude Code CLI skill for reviewing pending changes, a PR, or a branch. Renamed from `/review` (kept as alias) in v2.1.227; runs as a background subagent since v2.1.218. As of v2.1.215, no longer auto-runs on every turn — invoked explicitly or via `/code-review`.
