---
name: code-review
cmd: /code-review [PR#] [--fix] [--comment]
trigger: user asks to review PR, branch diff, or current changes
added: v2.1.147
---
Multi-pass code review with configurable effort and output modes.
- No arg: reviews current working diff
- `PR#`: reviews specified GitHub PR
- `--fix`: applies findings to working tree
- `--comment`: posts findings as inline PR review comments
- Effort levels: low/medium/high/max (default: medium)
