---
name: hookify-rules
description: Write hookify rules (.claude/hookify.<name>.local.md) to warn/block behaviors.
---
```
---
name: verb-kebab
enabled: true
event: bash|file|stop|prompt|all
pattern: python-regex      # or conditions: [{field, operator, pattern}]
action: warn|block         # default warn
---
Message shown to Claude.
```
`bash` matches command; `file` matches new_text of Edit/Write. Keep patterns narrow; test regex; toggle via `enabled`.
