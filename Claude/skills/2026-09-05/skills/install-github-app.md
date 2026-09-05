# Install GitHub App

- Slug: `install-github-app`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187` (CHANGELOG.md)
- Trigger: User wants Claude Code wired into GitHub PR/issue activity for a repo.

## Procedure

1. Run `/install-github-app`.
2. Choose whether to also set up the GitHub Actions workflow/secret, or install the App only (optional since v2.1.187).
3. GitHub-only: in a GitLab repo this points to the GitLab CI/CD docs instead (v2.1.259).

## Output

Claude GitHub App installed on the target repository.

## Token Policy

- One-time setup command; no recurring token cost.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Blocked only in background sessions with no client attached (v2.1.214+).

## Source Summary

> Improved `/install-github-app`: GitHub Actions workflow setup is now optional — you can install just the GitHub App and skip the workflow/secret steps.
