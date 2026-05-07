#!/usr/bin/env bash
# Sync changelogs and CLAUDE.md from repo to local machine.
# Run manually or via cron: 0 0 * * * /path/to/sync_changelogs.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-FdaL5"
CHANGELOGS_SRC="$REPO_DIR/Claude/Changelogs"
GLOBAL_CLAUDE_MD="${HOME}/.claude/CLAUDE.md"

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" pull origin "$BRANCH" --quiet

# Changelogs → desktop
mkdir -p "$DESKTOP_DIR"
if ls "$CHANGELOGS_SRC/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    echo "Changelogs synced: $(ls "$CHANGELOGS_SRC/"*.txt | wc -l) file(s) → $DESKTOP_DIR"
else
    echo "No changelogs found in Claude/Changelogs/."
fi

# CLAUDE.md → ~/.claude/CLAUDE.md (applies to all sessions globally)
if [ -f "$REPO_DIR/CLAUDE.md" ]; then
    mkdir -p "$(dirname "$GLOBAL_CLAUDE_MD")"
    cp -f "$REPO_DIR/CLAUDE.md" "$GLOBAL_CLAUDE_MD"
    echo "~/.claude/CLAUDE.md updated (all sessions)"
else
    echo "Warning: CLAUDE.md not found in repo."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
