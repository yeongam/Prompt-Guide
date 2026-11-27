---
name: code-modernization
description: Assess and migrate legacy code (language/framework uplift, rewrite, hardening). Use on "modernize", "migrate from X to Y", "legacy rewrite".
---
# Code Modernization
Src: claude-plugins-official/code-modernization@0fbfda5a91f4 (/modernize*)
Flow: preflight → assess → map → extract-rules → brief → (uplift | transform | reimagine) → harden → verify → review.
1. Locate system + current state (existing brief/status files first).
2. Assess size, deps, risk; extract business rules before changing code.
3. Write one brief (goal, target stack, constraints); show the step road.
4. Execute one step at a time; tests pin behavior before transforms.
5. Verify parity (tests/diff of behavior); record status.
