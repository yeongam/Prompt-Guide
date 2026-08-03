# Skill Creator

- Slug: `skill-creator`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Creating a new skill from scratch, editing/optimizing an existing one, running evals, or benchmarking skill trigger accuracy.

## Procedure

1. Clarify the skill's trigger conditions before writing content (avoid over- or under-triggering).
2. Keep the SKILL.md description precise and keyword-rich for correct matching.
3. Run evals/benchmarks when optimizing an existing skill rather than guessing at changes.

## Output

A new or improved skill definition with measured trigger accuracy.

## Token Policy

- Keep SKILL.md descriptions compact; move deep detail into reference files loaded on demand.

## Compatibility

- Meta-skill: used to build/maintain other skills in this catalog; no collision with existing entries.
