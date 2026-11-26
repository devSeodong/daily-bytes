#!/bin/bash
# launchd가 부르는 진입점.  run.sh collect | run.sh publish [public|private]
set -u
cd "$(dirname "$0")"
PY=${DB_PY:-/opt/homebrew/bin/python3.12}
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
DATE=$(date +%F)
LOG="$HOME/daily-bytes-bot/logs"; mkdir -p "$LOG"
exec >>"$LOG/$DATE.log" 2>&1
echo "===== $(date '+%F %T') $*"
case "${1:-}" in
  collect) "$PY" collect.py --date "$DATE" ;;
  publish)
    VIS=${2:-public}
    "$PY" thumb.py --date "$DATE" &&
    "$PY" publish.py --date "$DATE" --visibility "$VIS" &&
    { [ "$VIS" = public ] && "$PY" archive.py --date "$DATE" || true; } ;;
  *) echo "usage: run.sh collect|publish [public|private]"; exit 1 ;;
esac
echo "===== done rc=$?"
