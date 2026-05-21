#!/usr/bin/env bash
# Sync Claude/Changelogs from repo to local desktop path.
# Run manually or via cron: 0 15 * * * /path/to/sync_changelogs.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-S9nr0"

echo "[$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M KST')] Starting sync..."

git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" pull origin "$BRANCH" --quiet

mkdir -p "$DESKTOP_DIR"

CHANGELOGS_DIR="$REPO_DIR/Claude/Changelogs"

if ls "$CHANGELOGS_DIR/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOGS_DIR/"*.txt "$DESKTOP_DIR/"
    echo "Synced $(ls "$CHANGELOGS_DIR/"*.txt | wc -l) changelog(s) to $DESKTOP_DIR"
else
    echo "No changelogs found in $CHANGELOGS_DIR yet."
fi

echo "[$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M KST')] Sync complete."
