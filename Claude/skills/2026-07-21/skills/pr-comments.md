# PR Comments

- Slug: `pr-comments`
- Command: `/pr-comments`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user wants outstanding review comments on a PR triaged or answered

## Procedure

1. Fetch open review comments on the PR.
2. Address or reply to each with enough context to stand alone.
3. Skip duplicates or already-resolved threads silently.

## Output

Replies or fixes for outstanding PR review comments.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Reads and responds to pull request review comments; recent releases fixed the model selection used for this command.
