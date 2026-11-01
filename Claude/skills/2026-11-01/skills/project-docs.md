# project-docs (init, doctor, skill-doctor)
- `/init`: write CLAUDE.md = commands, architecture, conventions only; omit what is derivable from code (doctor flags this).
- `/doctor prompt-audit`: trim prompts written for older models (shouting, redundant rules).
- `/skill-doctor`: drop unused/costly skills; `skillOverrides: name-only` to cut context.
- Keep docs short; one canonical source, reference don't duplicate.
