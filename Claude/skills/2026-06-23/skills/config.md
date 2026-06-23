---
name: config
cmd: /config [key=value] [--help]
trigger: user wants to change a setting inline without editing settings.json
added: v2.1.181
---
Inline settings editor.
- `/config thinking=false`: toggle any setting key
- `/config --help`: list all available shorthand keys
- Enter/Space toggles booleans; Esc saves and closes interactive mode
