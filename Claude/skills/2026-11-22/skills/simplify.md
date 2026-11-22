---
name: simplify
description: Clean up changed code (reuse, simplification, efficiency, altitude) and apply fixes. Quality only, no bug hunt.
---
Cmd: `/simplify`
1. Scope: changed code only.
2. Look for: duplicate logic → reuse existing helper; dead code; needless abstraction; O(n²)→O(n); wrong layer.
3. Apply fixes; keep behavior identical; run tests if present.
Output: list of edits `file:line | change`. For bugs, use code-review.
