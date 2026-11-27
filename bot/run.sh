#!/bin/bash
# launchd(또는 AI 데일리 실행)가 부르는 진입점.  run.sh collect | run.sh publish [public|private]
# publish는 같은 날 여러 번 돌려도 안전: 커버는 있으면 재사용, 발행된 글은 건너뜀, 보관은 이미 있으면 건너뜀.
set -u
cd "$(dirname "$0")"
PY=${DB_BOT_PY:-$HOME/daily-bytes-bot/venv/bin/python}   # 봇 스크립트는 venv (last30days는 config.PY)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
DATE=$(date +%F)
LOG="$HOME/daily-bytes-bot/logs"; mkdir -p "$LOG"
exec >>"$LOG/$DATE.log" 2>&1
echo "===== $(date '+%F %T') $*"

# 같은 작업이 겹쳐 돌지 않게 (AI 실행 + 20:40 예비 실행)
LOCK="$HOME/daily-bytes-bot/.lock-${1:-x}"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +60 2>/dev/null)" ]; then rm -rf "$LOCK"; mkdir "$LOCK"
  else echo "다른 ${1:-} 실행 중이라 종료"; exit 0; fi
fi
trap 'rm -rf "$LOCK"' EXIT

# 일요일은 휴재 (요일제: 월·목 AI 이슈 / 화·금 개발 이슈 / 수·토 AI 트렌드)
if [ "$(date +%u)" = 7 ]; then echo "일요일 휴재 → 종료"; echo "===== done rc=0"; exit 0; fi

rc=0
case "${1:-}" in
  collect) "$PY" collect.py --date "$DATE"; rc=$? ;;
  publish)
    VIS=${2:-public}
    START=${DB_START:-2026-11-27}   # 공개 배치 시작일. 그 전에는 공개 발행 안 함
    if [ "$VIS" = public ] && [[ "$DATE" < "$START" ]]; then echo "공개 배치는 $START부터 → 건너뜀"; echo "===== done rc=0"; exit 0; fi
    "$PY" thumb.py --date "$DATE" && "$PY" publish.py --date "$DATE" --visibility "$VIS"; rc=$?
    if [ $rc -eq 0 ] && [ "$VIS" = public ]; then
      "$PY" archive.py --date "$DATE"; rc=$?
    elif [ $rc -ne 0 ]; then
      echo "발행 실패(rc=$rc) → 보관 건너뜀"
    fi ;;
  *) echo "usage: run.sh collect|publish [public|private]"; exit 1 ;;
esac
echo "===== done rc=$rc"
exit $rc
