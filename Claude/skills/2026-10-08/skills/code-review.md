# code-review (/code-review [low|medium|high|xhigh|max] [target] [--comment|--fix])
Use: correctness-bug review of diff/PR/branch/path. Replaces /simplify (renamed 2.1.x).
- effort picks finding count; medium also reports cleanup + CLAUDE.md rule findings.
- --comment: inline GitHub PR comments. --fix: apply findings.
- Inline lean prompts (no review-subagent fan-out) unless model has tuned settings.
- Alias: /review. Cleanup-only pass: /simplify (legacy, kept for compat).
