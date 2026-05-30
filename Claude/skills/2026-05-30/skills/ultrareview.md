# Ultrareview

- Slug: `ultrareview`
- Cmd: `/ultrareview [PR#]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user says "ultrareview" or wants multi-agent parallel code review
- Note: Billed; requires git repo; no GitHub remote needed for local mode

## Modes

| Mode | Command |
|------|---------|
| Local branch | `/ultrareview` (no arg) |
| GitHub PR | `/ultrareview 123` |

## Procedure

1. Spawn parallel review agents (logic / security / style / tests).
2. Each agent reviews independently.
3. Merge and deduplicate findings.
4. Risk-rank combined output.

## Output

Merged risk-ranked findings from all agents; agent count and coverage noted.

## Token Policy

- Deduplicate identical findings across agents.
- Return merged list only; no per-agent verbosity.
- Risk-rank: CRITICAL first.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
