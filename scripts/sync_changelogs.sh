#!/usr/bin/env bash
# Sync changelogs from repo to local desktop path.
# Run manually or via cron: 0 0 * * * /path/to/sync_changelogs.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-/root/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/kind-feynman-XQCh2"

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" pull origin "$BRANCH" --quiet

mkdir -p "$DESKTOP_DIR"

if ls "$REPO_DIR/changelogs/"*.txt 1>/dev/null 2>&1; then
    cp -u "$REPO_DIR/changelogs/"*.txt "$DESKTOP_DIR/"
    echo "Synced $(ls "$REPO_DIR/changelogs/"*.txt | wc -l) changelog(s) to $DESKTOP_DIR"
else
    echo "No changelogs found in repo yet."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
