# Commit Push PR

- Slug: `commit-push-pr`
- Command: `/commit-push-pr`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user wants to commit, push, and open a PR in one step

## Procedure

1. Stage the relevant files and write a descriptive commit message.
2. Push to the configured push remote (falls back to origin).
3. Open the PR and post its URL wherever configured (e.g. Slack via MCP).

## Output

A pushed commit and an opened pull request.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Auto-allows push to remote.pushDefault (or the sole remote) in addition to origin, and can post PR URLs to configured Slack channels.
