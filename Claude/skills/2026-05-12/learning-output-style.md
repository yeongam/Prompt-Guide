# learning-output-style
source: anthropics/claude-code/plugins/learning-output-style
updated: 2026-05-12

## Purpose
Transforms Claude sessions into active learning experiences by requesting user contributions at meaningful decision points.

## Activation
Auto-enabled at session start (SessionStart hook). No manual command.

## Behavior
- Claude identifies 5–10 line contribution opportunities: business logic, error handling, algorithms, design patterns
- Poses trade-off questions before implementing (e.g. "session timeout: hard vs. activity-based?")
- Provides ★ Insight blocks explaining implementation choices, patterns, trade-offs

## Claude implements directly (no contribution request)
Boilerplate, repetitive code, obvious implementations, configuration, simple CRUD.

## Management
Disable – keep code, stop running
Uninstall – remove entirely
Personalize – create local copy for customization
