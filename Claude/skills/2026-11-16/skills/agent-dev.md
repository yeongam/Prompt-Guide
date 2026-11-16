# Agent SDK / Plugin / API Development
src: claude-plugins-official/plugins/{agent-sdk-dev,plugin-dev} + builtin claude-api

## claude-api (builtin)
`/claude-api` sub: upgrade(py 0.x→1.x) · cost-optimize · latency-optimize · api-version · prompt-audit · managed-agents-{onboard,secure}

## agent-sdk-dev
- `/new-sdk-app [name]` — scaffold Agent SDK app (py|ts)
- agents: agent-sdk-verifier-py, agent-sdk-verifier-ts — check config + best practice

## plugin-dev
- `/plugin-dev:create-plugin` — guided: design → implement → validate
- skills (load on demand): plugin-structure · command-development · agent-development · skill-development · hook-development · mcp-integration · plugin-settings
- agents: plugin-validator · agent-creator · skill-reviewer
- CLI: `claude plugin init <name>` · `claude plugin validate`

## skill authoring rules (token-lean)
- frontmatter `description`: trigger phrases, 3rd person, ≤1 para
- SKILL.md body <500 lines; move detail to references/ (progressive disclosure)
- check cost with `/skill-doctor`
