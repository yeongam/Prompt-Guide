# deep-research

- Slug: `deep-research`
- Cmd: `/deep-research`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants multi-source, fact-checked research report.

## Procedure

1. Fan-out 3–5 parallel web searches.
2. Fetch top sources; verify claims adversarially.
3. Synthesize cited report with confidence levels.

## Output

Cited research report; contradictions flagged.

## Token Policy

- Fetch excerpts, not full HTML. Deduplicate sources.

## Compatibility

- Ask 2–3 clarifying questions if topic is underspecified.
