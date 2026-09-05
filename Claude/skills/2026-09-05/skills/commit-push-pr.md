# Commit Push PR

- Slug: `commit-push-pr`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.229` (CHANGELOG.md)
- Trigger: User wants to commit, push, and open a PR without separate manual steps.

## Procedure

1. Stage and commit with a descriptive message.
2. Push to the configured push remote (`remote.pushDefault`, or the sole remote when only one is configured).
3. Open the pull request; confirm before any dangerous flag is used.

## Output

Pushed branch plus opened pull request.

## Token Policy

- Single command replaces a multi-step git/gh sequence.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Never auto-approve `--force`/`--amend`/`--no-verify` (changed in v2.1.229).

## Source Summary

> `/commit-push-pr` now auto-allows `git push` to the repo's configured push remote in addition to `origin`. Dangerous flags are no longer auto-approved.
