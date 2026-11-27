---
name: project-docs
description: Produce project status pages, session usage reports, or interactive HTML playgrounds. Use on "project status page", "session token report", "make a playground".
---
# Project Docs
Src: claude-plugins-official/{project-artifact,session-report,playground}@0fbfda5a91f4
- status: tabs Overview(success criteria) · Workstreams · Next steps; add Background/Plan/Risks/Decisions only if they earn a tab; publish as private Artifact.
- session-report: parse `~/.claude/projects` transcripts → tokens, cache hit, subagents, skills, costliest prompts → one HTML file.
- playground: single self-contained HTML: controls → live preview → "copy prompt" output.
Concise prose; tables over paragraphs; cite sources.
