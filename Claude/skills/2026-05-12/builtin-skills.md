# builtin-skills
source: claude-code (built-in)
updated: 2026-05-12

## Skills (slash commands)

### /init
Generates CLAUDE.md with codebase documentation for new projects.

### /review
Reviews current branch PR. Analyzes diff, checks code quality, reports findings.

### /security-review
Full security audit of pending branch changes. OWASP-aware, reports vulnerabilities.

### /simplify
Reviews changed code for reuse, quality, efficiency; fixes issues found.

### /claude-api
Build/debug/optimize Claude API (Anthropic SDK) apps with prompt caching.
Handles: caching, thinking, tool use, batch, files, citations, memory, model migration.
Triggers on: anthropic / @anthropic-ai/sdk imports, Opus/Sonnet/Haiku model usage.

### /update-config
Configure Claude Code harness via settings.json.
Use for: automated behaviors (hooks), permissions, env vars.
Examples: "allow npm commands", "set DEBUG=true", "when claude stops show X"

### /keybindings-help
Customize keyboard shortcuts in ~/.claude/keybindings.json.
Examples: rebind ctrl+s, add chord shortcuts, change submit key.

### /session-start-hook
Set up SessionStart hook to run tests/linters at web session start.

### /fewer-permission-prompts
Scan transcripts for common read-only tool calls; add allowlist to .claude/settings.json.

### /loop [interval] [command]
Run a prompt/command on recurring interval (default 10m).
Example: /loop 5m /review
