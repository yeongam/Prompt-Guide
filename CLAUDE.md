# Skills v2.1.172 (2026-06-12)
> auto-updated from anthropics/claude-code — do not edit

`/init` | user asks to initialize or document codebase → Generate CLAUDE.md with codebase architecture, conventions, commands
`/review` | user asks to review PR or branch → Multi-pass PR review; checks logic, style, security, tests
`/security-review` | user asks security audit of current branch changes → OWASP-focused audit of pending diffs; outputs risk-ranked findings
`/simplify` | user asks to clean up or refactor changed code → Review changed code for reuse/quality/efficiency, then fix issues
`/session-start-hook` | user wants test/lint runners on session start (web Claude Code) → Create SessionStart hook ensuring project can run tests and linters
`/update-config` | automated behavior requests ("when X", "allow Y", "set Z=val") → Configure settings.json; handles hooks, permissions, env vars
`/keybindings-help` | user wants to remap keys or add chord shortcuts → Customize ~/.claude/keybindings.json; supports chord bindings
`/fewer-permission-prompts` | user wants fewer permission dialogs → Scan transcripts → add bash/MCP allowlist to .claude/settings.json
`/loop [interval] [/command]` | user wants recurring task (e.g. "check every 5m", "keep running X") → Run prompt or slash command on recurring interval (default 10m)
`/claude-api` | code imports anthropic SDK; user asks about Claude API features → Build/debug Claude API apps; prompt caching, tool use, model migration
`/ultrareview [PR#]` | user says "ultrareview" or wants multi-agent review → Parallel multi-agent cloud code review; billed; no-arg=local, arg=GitHub PR
`/ultraplan` | user wants cloud environment for complex planning → Auto-create cloud worktrees/environments for multi-agent planning tasks
`/team-onboarding` | user wants teammate ramp-up guide → Generate onboarding guide from local Claude Code usage history/data
`/effort` | user wants to adjust effort/quality level → Interactive slider for session effort level
`/powerup` | user wants feature demos or to learn Claude Code features → Interactive animated feature demos with lessons
`/tui` | rendering looks flickery or user wants full-screen mode → Switch to flicker-free alt-screen TUI rendering
`/focus` | user wants compact view of conversation → Toggle focus view showing only: prompt + tool summary + final response
`/undo` | user wants to undo last action → Rewind last assistant action
`/usage` | user asks about token or cost statistics → Show token usage and cost stats
`/theme [name]` | user wants to change or create visual theme → Create or switch custom color themes
`/color` | user wants a session color → Set random session color
`/login` | user needs to authenticate or switch Anthropic account → Authenticate Claude Code with Anthropic account credentials
`/status` | user wants to check Claude Code connection or account status → Show current account, model, and connection status
`/upgrade` | user wants to update Claude Code to the latest version → Upgrade Claude Code CLI to the latest release
`/mcp` | user wants to list, add, or inspect MCP servers → Manage MCP server connections: list, add, remove, inspect
`/terminal-setup` | user wants to configure terminal for optimal Claude Code experience → Configure terminal settings, shell integration, and display options
`/extra-usage` | user wants detailed token or cost breakdown beyond /usage → Show extended token usage stats with per-model and per-session breakdown
`/compact [instructions]` | user wants to compress conversation context or reduce token usage mid-session → Compress conversation history in-place to reduce token consumption; optional focus instructions
`/clear` | user wants to reset conversation context or start fresh → Clear entire conversation history to free context window for a new task
`/commit` | user asks to generate or improve a commit message → Auto-generate conventional commit message from staged diff
`/debug` | user asks to debug error, test failure, or unexpected behavior → Systematic debug loop: reproduce → trace → fix → verify
`/batch` | user wants to apply the same operation across multiple files → Batch edit or search across files matching a pattern or glob
`/model` | user wants to view or switch the active Claude model → Display or change the active model for this session
`/skills` | user wants to list available skills or commands → List all available skills, their triggers, and current version
`/plugin` | user wants to install, list, or remove a Claude Code plugin → Manage Claude Code plugins: install, list, remove
`/bug` | user wants to file a bug or investigate unexpected behavior → Structured bug report with steps to reproduce, expected vs actual, environment
`/api-design` | user asks to design or review API endpoints → Generate REST/GraphQL spec with validation, auth, consistent error responses
`/db-migrations` | user needs a database migration script → Write safe reversible migration with rollback and data integrity checks
`/docker-patterns` | user needs Dockerfile or container configuration → Multi-stage Dockerfile with security hardening and compose setup
`/deploy-patterns` | user asks about deployment or CI/CD pipeline setup → Scaffold CI/CD with rollback, health checks, blue-green or canary strategy
`/postgres-patterns` | user asks about PostgreSQL schema, query, or index design → Idiomatic Postgres: CTEs, proper indexing, constraints, explain plans
`/ts-review` | user asks to review TypeScript code → Type-safety review: strict nulls, generics, narrowing, interface design
`/py-review` | user asks to review Python code → Pythonic review: type hints, dataclasses, comprehensions, idiomatic error handling
`/go-patterns` | user needs Go code or idiomatic patterns → Idiomatic Go: error wrapping, goroutines, interfaces, zero-value design
`/search-first` | user wants to find existing code before writing new code → Search codebase for existing patterns before creating; prevents duplication
`/iterative-search` | user needs to locate something specific through progressive narrowing → Multi-pass search with narrowing queries until target is found
`/cost-aware` | user wants token- or cost-efficient operation → Choose minimal-token paths: targeted reads, diff views, concise outputs
`/auto-loops` | user wants to automate a repetitive multi-step coding task → Structured task loop: plan → execute → validate → repeat until complete
`/mcp-patterns` | user wants to build or configure an MCP server → Scaffold MCP server with tools, resources, prompts, proper error handling
`/kotlin-patterns` | user needs Kotlin code or architecture patterns → Idiomatic Kotlin: data classes, coroutines, extension functions, DSL patterns
`/kotlin-testing` | user needs to write Kotlin tests → Kotlin test suite with MockK, Kotest, coroutine test utilities
`/kotlin-coroutines-flows` | user asks about Kotlin coroutines or Flows → Coroutines + Flow patterns: structured concurrency, operators, cancellation
`/kotlin-exposed-patterns` | user needs Kotlin Exposed ORM code → Exposed DSL/DAO patterns with transactions and query optimization
`/kotlin-ktor-patterns` | user needs Ktor server or client code → Ktor routing, plugins, serialization, authentication patterns
`/rust-patterns` | user needs Rust code or architecture patterns → Idiomatic Rust: ownership, lifetimes, traits, error handling with Result
`/rust-testing` | user needs to write Rust tests → Rust test suite: unit, integration, mocking, property-based tests
`/csharp-testing` | user needs to write C# tests → C# test suite with xUnit/NUnit, Moq, FluentAssertions
`/dotnet-patterns` | user needs .NET architecture or patterns → .NET idiomatic patterns: DI, async/await, LINQ, minimal API
`/jpa-patterns` | user needs JPA or Hibernate ORM patterns → JPA entities, relationships, queries, N+1 prevention, transaction scope
`/swift-actor-persistence` | user needs Swift actor model with data persistence → Swift actors with CoreData/SwiftData; concurrency-safe persistence layer
`/swift-protocol-di-testing` | user needs Swift protocol-based DI or testing patterns → Protocol-oriented DI for testability; injectable mocks in Swift
`/swift-concurrency-6-2` | user needs Swift structured concurrency patterns → Swift 6.2 concurrency: actors, async/await, task groups, Sendable
`/swiftui-patterns` | user needs SwiftUI views or state management → SwiftUI patterns: ObservableObject, @State, MVVM, previews
`/pytorch-patterns` | user needs PyTorch model code or training loop → PyTorch patterns: modules, dataloaders, training loop, device handling
`/foundation-models-on-device` | user needs on-device ML inference on Apple silicon → Foundation Models API for local LLM inference; Apple silicon patterns
`/dart-flutter-patterns` | user needs Dart or Flutter code → Flutter/Dart patterns: widgets, state management, BLoC, Navigator 2.0
`/flutter-dart-code-review` | user asks to review Flutter or Dart code → Flutter review: widget rebuilds, state isolation, platform channels, performance
`/android-clean-architecture` | user needs Android architecture patterns → Android clean arch: MVVM, Hilt DI, Coroutines+Flow, Repository pattern
`/compose-multiplatform-patterns` | user needs Compose Multiplatform shared UI code → Compose Multiplatform: expect/actual, KMP setup, shared UI, platform APIs
`/nextjs-turbopack` | user needs Next.js App Router or Turbopack configuration → Next.js 15 App Router: RSC, server actions, Turbopack config, caching
`/nuxt4-patterns` | user needs Nuxt 4 code or configuration → Nuxt 4 patterns: auto-imports, composables, server routes, Nitro config
`/nestjs-patterns` | user needs NestJS backend code or architecture → NestJS patterns: modules, providers, interceptors, guards, TypeORM/Prisma
`/laravel-plugin-discovery` | user needs Laravel package or plugin code → Laravel package discovery, service providers, facades, Artisan commands
`/clickhouse-io` | user needs ClickHouse schema or query optimization → ClickHouse MergeTree design, materialized views, query optimization

catalog: Claude/skills/SKILLS_CATALOG.yaml | commands: .claude/commands/
