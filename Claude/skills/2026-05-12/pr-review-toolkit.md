# pr-review-toolkit
source: anthropics/claude-code/plugins/pr-review-toolkit
updated: 2026-05-12

## Purpose
6 specialized agents for comprehensive PR analysis.

## Agents
| Agent               | Focus                        |
|---------------------|------------------------------|
| comment-analyzer    | Documentation accuracy       |
| pr-test-analyzer    | Test coverage quality        |
| silent-failure-hunter | Error handling gaps        |
| type-design-analyzer| Type design quality          |
| code-reviewer       | General code quality         |
| code-simplifier     | Clarity & refactoring        |

## Workflow
- Before commit: code-reviewer + silent-failure-hunter
- Before PR: pr-test-analyzer + comment-analyzer + type-design-analyzer + code-reviewer
- After review pass: code-simplifier for polish

## Output format
Structured findings with file references, severity scores, improvement suggestions.
