# Coding / Programming
src: claude-plugins-official/plugins/{feature-dev,commit-commands,frontend-design,ralph-loop,hookify}

## feature-dev  `/feature-dev <desc>`
when: new feature in existing code
flow: explore(code-explorer) → clarify → design(code-architect, 2-3 options) → implement → review(code-reviewer) → summary
rule: ask before implementing; follow repo conventions

## commit-commands
- `/commit` — stage + commit with repo-style message
- `/commit-push-pr` — commit, push branch, open PR
- `/clean_gone` — delete local branches marked [gone] (+ worktrees)

## frontend-design (skill)
when: building/reshaping UI
rule: pick one bold aesthetic direction; distinctive type, cohesive palette, purposeful motion; avoid generic defaults

## ralph-loop
- `/ralph-loop "<task>" --completion-promise "<text>" [--max-iterations N]` — Stop hook re-feeds same prompt until promise output
- `/cancel-ralph` — stop
note: prefer builtin `/goal` for simple cases (lower overhead)

## hookify
- `/hookify [instruction]` — make rule from transcript or instruction (.claude/hookify.*.local.md)
- `/hookify:list` `/hookify:configure` `/hookify:help`
rule fields: event(bash|file|stop|prompt|all), pattern, action(warn|block)
