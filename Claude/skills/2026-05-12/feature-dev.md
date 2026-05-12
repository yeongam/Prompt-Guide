# feature-dev
source: anthropics/claude-code/plugins/feature-dev
updated: 2026-05-12

## Purpose
7-phase guided workflow for building new features with multi-agent architecture design.

## Command
/feature-dev [feature description]

## Phases
1. Discovery – clarify requirements & constraints
2. Codebase Exploration – parallel code-explorer agents scan existing patterns
3. Clarifying Questions – resolve ambiguities before design
4. Architecture Design – code-architect agents present 2–3 approaches with trade-offs
5. Implementation – build after explicit approval, following chosen architecture
6. Quality Review – parallel code-reviewer agents (simplicity, correctness, conventions)
7. Summary – document decisions, modified files, next steps

## Agents
- code-explorer: traces execution paths, architecture patterns
- code-architect: designs implementations with rationale
- code-reviewer: flags bugs and convention violations with confidence scores
