# Documentation / Output Style
src: builtin + claude-plugins-official/plugins/{explanatory-output-style,learning-output-style}

## builtin
- `/init` — CLAUDE.md from codebase (AGENTS.md used if no CLAUDE.md)
- `/doctor` — streams findings; proposes trimming CLAUDE.md content derivable from code
- `/doctor prompt-audit` — flag outdated prompting patterns in CLAUDE.md/skills/agents
- `/output-style [name]` — switch style

## explanatory-output-style (SessionStart hook)
adds "Insight" notes on implementation choices. cost: extra tokens every turn → enable only when learning

## learning-output-style (SessionStart hook)
asks user to write key code pieces at decision points. same cost note

## doc skill rules
- keep CLAUDE.md to non-derivable facts (commands, conventions, gotchas)
- link docs instead of copying
