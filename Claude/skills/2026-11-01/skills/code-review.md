# code-review (+simplify, security-review)
Use: review diff/PR for correctness. `/code-review <level> [PR#] [--comment|--fix] [--max-findings n|all]`
- Level: low=few sure findings … max=many (explicit request only). `ultra`=cloud deep review.
- Steps: scope diff → find bugs (logic, edge, security, tests) → verify each → report ranked by severity: file:line, defect, failing scenario.
- `--comment` inline PR comments; `--fix` apply to tree.
- Cleanup (reuse/simplify/efficiency, applies fixes): /simplify. Security-only: /security-review.
- Don't merge/approve; no tests skipped to pass.
