---
name: feature-dev
description: Guided feature implementation grounded in the existing codebase. Use on "build feature X", "add support for Y".
---
# Feature Dev
Src: claude-plugins-official/feature-dev@0fbfda5a91f4
1. Discover: restate goal + acceptance criteria.
2. Explore: 2-3 parallel explorers trace similar features; read the files they return.
3. Clarify: ask only blocking questions (skip in automation; choose safest default).
4. Design: 1 recommended architecture + trade-off in ≤5 lines.
5. Implement: follow local conventions; smallest diff.
6. Review: run narrowest tests; self-review for bugs/simplicity.
7. Summary: what changed, files, follow-ups.
