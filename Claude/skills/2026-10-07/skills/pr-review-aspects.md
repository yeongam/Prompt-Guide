---
name: pr-review-aspects
description: Targeted PR review by aspect: comments, tests, errors, types, code, simplify, all.
---
Scope = `git diff --name-only` (+`gh pr view`). Run only applicable agents:
- code (always): CLAUDE.md/bugs/quality
- tests if tests changed: behavioral coverage gaps
- comments if docs/comments added: accuracy, comment rot
- errors if error handling changed: silent failures, catch blocks
- types if types added: encapsulation, invariants
- simplify after clean review: clarity, behavior-preserving
Sequential by default; parallel if asked. Report: Critical / Important / Suggestions / Strengths with file:line, then action plan. Run before PR; rerun after fixes.
