#!/usr/bin/env bash
# Register daily midnight cron job for changelog sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_changelogs.sh"
LOG_FILE="/var/log/claude-skills-sync.log"

chmod +x "$SYNC_SCRIPT"

CRON_ENTRY="0 0 * * * $SYNC_SCRIPT >> $LOG_FILE 2>&1"
CLEAN_CRON=$(crontab -l 2>/dev/null | grep -v "sync_changelogs" || true)

echo "$CLEAN_CRON"$'\n'"$CRON_ENTRY" | crontab -

echo "Cron job registered:"
echo "  $CRON_ENTRY"
echo ""
echo "To verify: crontab -l"
echo "To view logs: tail -f $LOG_FILE"
