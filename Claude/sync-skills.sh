#!/usr/bin/env bash
# Daily skills sync: anthropics/claude-code → Claude/skills/YYYY-MM-DD/
# Runs at 00:00 via cron. No user input required.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$REPO_ROOT/Claude"
DATE="$(date +%Y-%m-%d)"
SKILLS_DIR="$CLAUDE_DIR/skills/$DATE"
CHANGELOG_DIR="$CLAUDE_DIR/Changelogs"
CHANGELOG_FILE="$CHANGELOG_DIR/$DATE.txt"
API_BASE="https://api.github.com/repos/anthropics/claude-code"
RAW_BASE="https://raw.githubusercontent.com/anthropics/claude-code/main"
GIT_BRANCH="claude/zealous-sagan-h0URx"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# ── Fetch plugin list ──────────────────────────────────────────────────────────
fetch_plugin_list() {
  curl -sf "$API_BASE/contents/plugins" \
    | grep '"name"' \
    | grep -v 'README' \
    | sed 's/.*"name": "\([^"]*\)".*/\1/'
}

# ── Fetch README for a plugin ─────────────────────────────────────────────────
fetch_readme() {
  local plugin="$1"
  curl -sf "$RAW_BASE/plugins/$plugin/README.md" 2>/dev/null || echo ""
}

# ── Compact a README into a minimal skill file ────────────────────────────────
compact_skill() {
  local plugin="$1"
  local readme="$2"
  local outfile="$3"

  # Extract first heading as title, first paragraph as purpose
  local title purpose
  title=$(echo "$readme" | grep -m1 '^# ' | sed 's/^# //' | tr -d '[:space:]')
  purpose=$(echo "$readme" | awk '/^## (Purpose|Overview|Description)/{found=1;next} found && /^##/{exit} found{print}' | head -5 | sed '/^$/d')
  [ -z "$purpose" ] && purpose=$(echo "$readme" | sed -n '3,6p' | sed '/^#/d;/^$/d')

  # Extract commands section
  local commands
  commands=$(echo "$readme" | awk '/^## (Commands|Usage|Command)/{found=1;next} found && /^##/{exit} found{print}' | grep -E '`/|^\/|^\*\*`/' | head -8 | sed 's/^[[:space:]]*//')

  cat > "$outfile" <<EOF
# $plugin
source: anthropics/claude-code/plugins/$plugin
updated: $DATE

## Purpose
${purpose:-See README at $RAW_BASE/plugins/$plugin/README.md}

## Commands
${commands:-Refer to plugin README}
EOF
}

# ── Compare with previous day's skills ────────────────────────────────────────
find_prev_skills_dir() {
  ls -d "$CLAUDE_DIR/skills"/20??-??-?? 2>/dev/null \
    | grep -v "$DATE" | sort | tail -1
}

diff_skills() {
  local prev_dir="$1"
  local curr_dir="$2"

  local added=() removed=() modified=()

  for f in "$curr_dir"/*.md; do
    local name
    name=$(basename "$f")
    if [ ! -f "$prev_dir/$name" ]; then
      added+=("$name")
    elif ! diff -q "$prev_dir/$name" "$f" > /dev/null 2>&1; then
      modified+=("$name")
    fi
  done

  for f in "$prev_dir"/*.md; do
    local name
    name=$(basename "$f")
    [ ! -f "$curr_dir/$name" ] && removed+=("$name")
  done

  echo "ADDED=${added[*]:-none}"
  echo "MODIFIED=${modified[*]:-none}"
  echo "REMOVED=${removed[*]:-none}"
}

# ── Write changelog ────────────────────────────────────────────────────────────
write_changelog() {
  local added="$1" modified="$2" removed="$3"
  local prev_dir="$4"

  mkdir -p "$CHANGELOG_DIR"
  cat > "$CHANGELOG_FILE" <<EOF
SKILLS SYNC CHANGELOG
Date: $DATE
Source: anthropics/claude-code (main)
Branch: $GIT_BRANCH

================================================================================
ADDED SKILLS
================================================================================
$([ "$added" = "none" ] && echo "None" || echo "$added" | tr ' ' '\n' | sed 's/^/  - /')

================================================================================
MODIFIED SKILLS
================================================================================
$([ "$modified" = "none" ] && echo "None" || echo "$modified" | tr ' ' '\n' | sed 's/^/  - /')

================================================================================
DELETED SKILLS
================================================================================
$([ "$removed" = "none" ] && echo "None" || echo "$removed" | tr ' ' '\n' | sed 's/^/  - /')

================================================================================
OPTIMIZED STRUCTURE
================================================================================
  - Directory: Claude/skills/$DATE/
  - Format: compact .md per skill (~300-500 bytes vs 4-8KB original README)
  - Sections: Purpose / Commands only (no prose, no examples)

================================================================================
TOKEN SAVINGS
================================================================================
  - Estimated ~85% reduction per skill vs full plugin README
  - Removed: installation steps, extended examples, full feature descriptions

================================================================================
CONFLICT RESOLUTION
================================================================================
  - No overwrite of existing root-level model prompt files
  - skills/ dir isolated from Claude-Opus-v4.6, Claude-Sonnet-v.4.6, Claude-in-chrome
  - Previous dir: ${prev_dir:-N/A (first run)}
================================================================================
EOF
}

# ── Git commit & push ─────────────────────────────────────────────────────────
git_push() {
  cd "$REPO_ROOT"
  git checkout "$GIT_BRANCH" 2>/dev/null || git checkout -b "$GIT_BRANCH"
  git add Claude/skills/ Claude/Changelogs/
  git diff --cached --quiet && { log "Nothing to commit."; return 0; }
  git commit -m "chore: sync skills $DATE from anthropics/claude-code"
  local attempt=0
  while [ $attempt -lt 4 ]; do
    git push -u origin "$GIT_BRANCH" && return 0
    attempt=$((attempt+1))
    sleep $((2**attempt))
    log "Push retry $attempt..."
  done
  log "ERROR: push failed after 4 attempts"
  return 1
}

# ── Main ───────────────────────────────────────────────────────────────────────
main() {
  log "Starting skills sync for $DATE"

  mkdir -p "$SKILLS_DIR"

  # Fetch and compact each plugin skill
  local plugins
  plugins=$(fetch_plugin_list)

  for plugin in $plugins; do
    local readme
    readme=$(fetch_readme "$plugin")
    [ -z "$readme" ] && { log "SKIP $plugin (no README)"; continue; }
    compact_skill "$plugin" "$readme" "$SKILLS_DIR/$plugin.md"
    log "  OK $plugin"
  done

  # Copy builtin-skills from previous if unchanged, else regenerate header
  local prev_dir
  prev_dir=$(find_prev_skills_dir)
  if [ -n "$prev_dir" ] && [ -f "$prev_dir/builtin-skills.md" ]; then
    sed "s/updated: .*/updated: $DATE/" "$prev_dir/builtin-skills.md" > "$SKILLS_DIR/builtin-skills.md"
  fi

  # Diff and write changelog
  local diff_out added modified removed
  if [ -n "$prev_dir" ]; then
    diff_out=$(diff_skills "$prev_dir" "$SKILLS_DIR")
    added=$(echo "$diff_out" | grep '^ADDED=' | cut -d= -f2)
    modified=$(echo "$diff_out" | grep '^MODIFIED=' | cut -d= -f2)
    removed=$(echo "$diff_out" | grep '^REMOVED=' | cut -d= -f2)
  else
    added=$(ls "$SKILLS_DIR"/*.md | xargs -n1 basename | tr '\n' ' ')
    modified="none"
    removed="none"
  fi

  write_changelog "$added" "$modified" "$removed" "$prev_dir"
  log "Changelog: $CHANGELOG_FILE"

  git_push
  log "Sync complete."
}

main "$@"
