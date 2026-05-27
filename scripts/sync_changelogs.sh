#!/usr/bin/env bash
# Sync changelogs from repo to local desktop path.
# Run manually or via cron: 0 0 * * * /path/to/sync_changelogs.sh
set -euo pipefail

REPO_DIR="${DESKTOP_LOG_PATH:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-vmY17"

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

git -C "$REPO_ROOT" fetch origin "$BRANCH" --quiet
git -C "$REPO_ROOT" pull origin "$BRANCH" --quiet

mkdir -p "$DESKTOP_DIR"

CHANGELOG_SRC="$REPO_ROOT/Claude/Changelogs"
if ls "$CHANGELOG_SRC/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOG_SRC/"*.txt "$DESKTOP_DIR/"
    echo "Synced $(ls "$CHANGELOG_SRC/"*.txt | wc -l) changelog(s) to $DESKTOP_DIR"
else
    echo "No changelogs found yet."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
