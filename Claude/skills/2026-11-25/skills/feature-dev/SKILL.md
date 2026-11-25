---
name: feature-dev
description: Implement a feature end to end. Use for multi-file features or unfamiliar codebases.
---
1. Explore: read CLAUDE.md/AGENTS.md, locate entry points (Explore agent for broad sweeps only).
2. Plan: smallest change that fits existing patterns; list files touched.
3. Implement: edit in place, match naming/style; no speculative abstractions.
4. Verify: narrowest test/lint command; then `/code-review low`.
Plugin equivalent: `feature-dev` (claude-plugins-official).
