#!/usr/bin/env bash
# Sync: pull latest from remote → run update_skills.py → copy changelogs to desktop.
# Registered via setup_local_cron.sh (cron: 0 0 * * *)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-FdaL5"
CHANGELOGS_SRC="$REPO_DIR/Claude/Changelogs"

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

# 1. Pull latest from remote
git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" pull origin "$BRANCH" --quiet

# 2. Run update_skills.py — handles ~/.claude/CLAUDE.md (guidelines 1순위 + skills 2순위)
#    and refreshes .claude/commands/
python3 "$REPO_DIR/scripts/update_skills.py"

# 3. Copy changelogs to desktop
mkdir -p "$DESKTOP_DIR"
if ls "$CHANGELOGS_SRC/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    echo "Changelogs synced: $(ls "$CHANGELOGS_SRC/"*.txt | wc -l) file(s) → $DESKTOP_DIR"
else
    echo "No changelogs in Claude/Changelogs/ yet."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
