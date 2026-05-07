#!/usr/bin/env bash
# Sync: pull latest from remote → run update_skills.py → copy changelogs to desktop.
# Registered via setup_local_cron.sh (cron: 0 0 * * *)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="${DESKTOP_LOG_PATH:-$HOME/바탕화면/Claude-Text/Claude_skills}"
BRANCH="claude/zealous-sagan-FdaL5"
CHANGELOGS_SRC="$REPO_DIR/Claude/Changelogs"
DATE_STR=$(date -u '+%Y%m%d')
RUN_LOG="$DESKTOP_DIR/run_log_${DATE_STR}.txt"

# cron 환경에서 python3 경로 탐색
PYTHON3=$(command -v python3 2>/dev/null \
    || ls /usr/local/bin/python3 /opt/homebrew/bin/python3 /usr/bin/python3 2>/dev/null | head -1 \
    || echo "")
if [ -z "$PYTHON3" ]; then
    echo "ERROR: python3를 찾을 수 없습니다." >&2
    exit 1
fi

# 이후 모든 출력을 화면 + 날짜별 txt 파일에 동시 저장
mkdir -p "$DESKTOP_DIR"
exec > >(tee -a "$RUN_LOG") 2>&1

echo "========================================"
echo "Claude Skills Sync Log"
echo "Date : $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "Repo : $REPO_DIR"
echo "========================================"

# 1. Pull latest from remote (remote-authoritative branch)
git -C "$REPO_DIR" fetch origin "$BRANCH" --quiet
git -C "$REPO_DIR" checkout "$BRANCH" --quiet 2>/dev/null \
    || git -C "$REPO_DIR" checkout -b "$BRANCH" --track "origin/$BRANCH" --quiet
git -C "$REPO_DIR" reset --hard "origin/$BRANCH" --quiet
echo "Branch  : $BRANCH synced"

# 2. Run update_skills.py — handles ~/.claude/CLAUDE.md (guidelines 1순위 + skills 2순위)
"$PYTHON3" "$REPO_DIR/scripts/update_skills.py"

# 3. Copy changelogs to desktop (rsync: cross-platform, skips unchanged files)
if ls "$CHANGELOGS_SRC/"*.txt 1>/dev/null 2>&1; then
    if command -v rsync &>/dev/null; then
        rsync -u "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    else
        cp "$CHANGELOGS_SRC/"*.txt "$DESKTOP_DIR/"
    fi
    echo "Changelogs synced: $(ls "$CHANGELOGS_SRC/"*.txt | wc -l) file(s) → $DESKTOP_DIR"
else
    echo "No changelogs in Claude/Changelogs/ yet."
fi

echo "========================================"
echo "Log saved : $RUN_LOG"
echo "Sync complete : $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "========================================"
