#!/usr/bin/env bash
# Sync: pull latest from remote → run update_skills.py → copy changelogs to desktop.
# Registered via setup_local_cron.sh (cron: 0 0 * * *)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-$HOME/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-FdaL5"
CHANGELOGS_SRC="$REPO_DIR/Claude/Changelogs"

# cron 환경에서 python3 경로 탐색
PYTHON3=$(command -v python3 2>/dev/null \
    || ls /usr/local/bin/python3 /opt/homebrew/bin/python3 /usr/bin/python3 2>/dev/null | head -1 \
    || echo "")
if [ -z "$PYTHON3" ]; then
    echo "ERROR: python3를 찾을 수 없습니다." >&2
    exit 1
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Starting sync..."

# 1. Pull latest from remote (reset to remote — this branch is remote-authoritative)
git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" reset --hard "origin/$BRANCH" --quiet

# 2. Run update_skills.py — handles ~/.claude/CLAUDE.md (guidelines 1순위 + skills 2순위)
"$PYTHON3" "$REPO_DIR/scripts/update_skills.py"

# 3. Copy changelogs to desktop
mkdir -p "$DESKTOP_DIR"
if ls "$CHANGELOGS_SRC/"*.txt 1>/dev/null 2>&1; then
    cp -u "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    echo "Changelogs synced: $(ls "$CHANGELOGS_SRC/"*.txt | wc -l) file(s) → $DESKTOP_DIR"
else
    echo "No changelogs in Claude/Changelogs/ yet."
fi

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete."
