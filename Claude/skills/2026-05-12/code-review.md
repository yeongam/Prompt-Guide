# code-review
source: anthropics/claude-code/plugins/code-review
updated: 2026-05-12

## Purpose
Multi-agent PR review with confidence-scored issue filtering.

## Command
/code-review [--comment]

## Behavior
1. Skip closed/draft/trivial/already-reviewed PRs
2. Collect CLAUDE.md guidelines from repo
3. Summarize PR diff
4. Run 4 parallel agents:
   - 2× CLAUDE.md compliance
   - 1× bug detection (changed lines only)
   - 1× git blame context analysis
5. Score each issue 0–100; discard < 80
6. Output high-confidence findings

## Options
--comment  Post results as PR comment (default: terminal output)

## Requirements
- GitHub CLI (gh) authenticated
- Optional: CLAUDE.md for guideline compliance checks
