# code-review
cmd: /code-review [--comment] [--fix] [low|medium|high|max]
trigger: user asks to review code diff, check for bugs, or find cleanup opportunities
desc: Review current diff for correctness bugs and reuse/simplification/efficiency cleanups
  effort: low/medium → fewer high-confidence findings; high/max → broader, may include uncertain findings
  --comment: post findings as inline PR comments
  --fix: apply findings to working tree after review
