# Autofix PR

- Slug: `autofix-pr`
- Command: `/autofix-pr`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user wants an existing PR's failures (e.g. failing CI) diagnosed and fixed

## Summary

Diagnoses and fixes issues on an already-open PR. Works correctly when the
session is inside a git worktree or a different repository than the PR's
own checkout (earlier versions incorrectly reported "cannot run on the
default branch" in that case).

## Token Policy

- Single reference card; do not duplicate CI-log content into the model context beyond what's needed to diagnose.

## Compatibility

- Complements `/code-review`; autofix-pr targets CI/PR-state failures, code-review targets code-quality findings.
