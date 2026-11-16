# Code Review / Security
src: claude-plugins-official/plugins/{code-review,pr-review-toolkit,security-guidance}

## builtin first (no install, lowest tokens)
`/code-review [level] [pr#] [--comment|--fix]` · `/simplify` · `/security-review`

## code-review plugin  `/code-review` (PR)
flow: parallel agents (CLAUDE.md compliance, bugs) → per-issue validation subagents → post validated only
conflict: same name as builtin → plugin form is namespaced `/code-review:code-review`

## pr-review-toolkit  `/review-pr [aspects]`
aspects → agent:
- comments → comment-analyzer
- tests → pr-test-analyzer
- errors → silent-failure-hunter
- types → type-design-analyzer
- code → code-reviewer
- simplify → code-simplifier
tip: pass only needed aspects to cut agent count

## security-guidance (hooks)
UserPromptSubmit/PostToolUse: pattern warnings (eval, innerHTML, pickle, child_process, GH Actions injection)
Stop: git-diff LLM security review (needs python; SessionStart installs Agent SDK)
