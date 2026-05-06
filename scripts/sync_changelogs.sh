#!/usr/bin/env bash
# Sync changelogs from Claude/Changelogs/ to local desktop path.
# Run manually or via cron: 0 0 * * * /path/to/sync_changelogs.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-FdaL5"
CHANGELOGS_SRC="$REPO_DIR/Claude/Changelogs"

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" pull origin "$BRANCH" --quiet

mkdir -p "$DESKTOP_DIR"

if ls "$CHANGELOGS_SRC/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    echo "Synced $(ls "$CHANGELOGS_SRC/"*.txt | wc -l) changelog(s) to $DESKTOP_DIR"
else
    echo "No changelogs found yet in Claude/Changelogs/."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
