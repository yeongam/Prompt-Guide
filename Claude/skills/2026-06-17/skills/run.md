# run
cmd: /run
trigger: user asks to run, start, or screenshot the app; confirm a change works in real app (not just tests)
desc: Launch and drive project app to observe behavior; checks for project-specific launch skill first
  fallback: built-in patterns per type (CLI, server, TUI, Electron, browser-driven, library)
