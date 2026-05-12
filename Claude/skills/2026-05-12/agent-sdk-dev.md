# agent-sdk-dev
source: anthropics/claude-code/plugins/agent-sdk-dev
updated: 2026-05-12

## Purpose
Scaffold and verify Claude Agent SDK applications (Python/TypeScript).

## Command
/new-sdk-app [project-name]

## Scaffolding prompts
- Language: Python or TypeScript
- Agent type, starting point, tooling preferences
- Installs latest SDK, generates config, runs type check
- Auto-runs verifier agent after setup

## Verifier agents
agent-sdk-verifier-py  – checks: SDK install, env, patterns, init, security, error handling, docs
agent-sdk-verifier-ts  – checks: SDK install, TS config, type safety, init, security, error handling

## Output
Status report: PASS / PASS WITH WARNINGS / FAIL + recommendations
