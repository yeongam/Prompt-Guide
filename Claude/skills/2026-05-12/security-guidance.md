# security-guidance
source: anthropics/claude-code/plugins/security-guidance
updated: 2026-05-12

## Purpose
Hook-based security guardrails that intercept potentially dangerous operations.

## Activation
Hook-driven (no manual command). Activates on matching tool events.

## Scope
Intercepts tool calls matching security-sensitive patterns and injects guidance or blocks execution based on configured rules.

## Configuration
Located in: plugins/security-guidance/hooks/
Customize rules to match project-specific security requirements.
