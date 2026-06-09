# Deep Research

- Slug: `deep-research`
- Source: anthropics/claude-code (built-in skill)
- Trigger: User wants multi-source, fact-checked research report on any topic.

## Procedure

1. Check if the question is specific enough; if underspecified, ask 2-3 clarifying questions.
2. Fan-out parallel web searches across multiple sources.
3. Fetch and verify primary sources.
4. Adversarially check claims against contradicting sources.
5. Synthesize a cited report with source URLs.

## Output

Structured research report with citations. Sources section is mandatory.

## Token Policy

- Cite source URLs instead of quoting full content.
- Summarize rather than reproduce large documents.
- One finding per bullet; no redundant background.

## Compatibility

- Available in all Claude Code environments with web access.
- No conflict with existing skills.
