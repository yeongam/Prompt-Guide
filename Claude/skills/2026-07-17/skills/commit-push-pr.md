# Commit Push PR

- Slug: `commit-push-pr`
- Command: `/commit-push-pr`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user wants to commit staged/working changes, push, and open a PR in one step

## Summary

Runs commit → push → PR creation as a single flow. Auto-allows `git push` to
the repo's configured `remote.pushDefault` (or the sole remote when only one
is configured), in addition to `origin` — avoids an extra permission prompt
on repos that don't push to `origin`.

## Token Policy

- One card, no per-step restating; the command already sequences the three steps.

## Compatibility

- Does not change existing manual git-commit workflows; purely additive.
