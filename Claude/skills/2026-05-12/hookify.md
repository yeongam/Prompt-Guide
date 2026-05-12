# hookify
source: anthropics/claude-code/plugins/hookify
updated: 2026-05-12

## Purpose
Create Claude Code hooks via markdown config to block or warn on unwanted behaviors.

## Commands
/hookify [description]    – Create rule from description or analyze conversation
/hookify:list             – Show all active rules
/hookify:configure        – Interactive rule management
/hookify:help             – Command docs

## Examples
"Warn me when I use rm -rf commands"
"Don't use console.log in TypeScript files"

## Rule format
YAML frontmatter + markdown message in .claude/hookify.[name].local.md

## Actions
warn   – allow operation with warning
block  – prevent execution

## Triggers
bash | file | stop | prompt | all

## Pattern matching
Python regex syntax; supports regex_match, contains, not_contains operators.
Rules take effect immediately (no restart required).
