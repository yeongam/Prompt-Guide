# explanatory-output-style
source: anthropics/claude-code/plugins/explanatory-output-style
updated: 2026-05-12

## Purpose
Injects educational context into Claude sessions via SessionStart hook (recreates deprecated output style).

## Activation
Auto-enabled at session start. No manual command.

## Injected behavior
- Explains implementation choices specific to the codebase
- Describes patterns and conventions found in the code
- Highlights trade-offs and design decisions

## Output format
Visual separator box for insight blocks.

## Note
Each session incurs extra token cost from injected instructions.

## Management
Disable – keep code, stop running
Uninstall – remove entirely
Personalize – create local copy for customization
