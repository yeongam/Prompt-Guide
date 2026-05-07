#!/usr/bin/env bash
# Register daily midnight sync via systemd timer (preferred) or crontab fallback.
# Run ONCE on your actual local machine — not sandbox/CI.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYNC_SCRIPT="$REPO_DIR/scripts/sync_changelogs.sh"
LOG_FILE="/var/log/claude-skills-sync.log"

chmod +x "$SYNC_SCRIPT"

# ── systemd timer (Ubuntu/Debian with systemd as PID 1) ──────────────────────
if command -v systemctl &>/dev/null && [ "$(cat /proc/1/comm 2>/dev/null)" = "systemd" ]; then
    SERVICE=/etc/systemd/system/claude-skills-sync.service
    TIMER=/etc/systemd/system/claude-skills-sync.timer

    cat > "$SERVICE" <<EOF
[Unit]
Description=Claude Code Skills Daily Sync
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
WorkingDirectory=$REPO_DIR
ExecStart=/bin/bash $SYNC_SCRIPT
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE
EOF

    cat > "$TIMER" <<EOF
[Unit]
Description=Claude Code Skills Daily Sync Timer
Requires=claude-skills-sync.service

[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable --now claude-skills-sync.timer
    echo "systemd timer registered: claude-skills-sync.timer"
    echo "  Status : systemctl status claude-skills-sync.timer"
    echo "  Logs   : journalctl -u claude-skills-sync.service"

# ── crontab fallback ──────────────────────────────────────────────────────────
elif command -v crontab &>/dev/null; then
    CRON_ENTRY="0 0 * * * $SYNC_SCRIPT >> $LOG_FILE 2>&1"
    CLEAN=$(crontab -l 2>/dev/null | grep -v "sync_changelogs" || true)
    echo "$CLEAN"$'\n'"$CRON_ENTRY" | crontab -
    echo "crontab registered: $CRON_ENTRY"
    echo "  Verify : crontab -l"
    echo "  Logs   : tail -f $LOG_FILE"

else
    echo "ERROR: 스케줄러 없음 (systemd PID1 아님 + crontab 없음)"
    echo "  수동 실행: bash $SYNC_SCRIPT"
    exit 1
fi
