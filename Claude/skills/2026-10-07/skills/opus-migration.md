---
name: opus-migration
description: Migrate Sonnet 4/4.5, Opus 4.1 model strings and prompts to Opus 4.5. Not Haiku. Check claude-api skill for newer models first.
---
1. Grep model strings/API calls. 2. Replace: 1P/Azure `claude-opus-4-5-20251101`; Bedrock `anthropic.claude-opus-4-5-20251101-v1:0`; Vertex `claude-opus-4-5@20251101`.
Sources: `claude-sonnet-4-20250514`, `claude-sonnet-4-5-20250929`, `claude-opus-4-1-20250422` (+Bedrock/Vertex forms).
3. Remove beta `context-1m-2025-08-07` (comment why). 4. Set effort `"high"`. 5. Summarize.
Prompt fixes only if issue reported: overtriggering tools (soften CRITICAL/MUST/ALWAYS/NEVER), over-engineering, no code exploration, generic frontend, "think" wording without `thinking` param ("consider"/"evaluate"). Integrate via XML tags in existing style.
