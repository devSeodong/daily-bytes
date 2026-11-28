"""맥 미니 배치 공통 설정. 경로는 환경변수로 바꿀 수 있어요."""
import os
from pathlib import Path

HOME = Path.home()
BOT = Path(os.environ.get("DB_BOT_HOME", HOME / "daily-bytes-bot"))
WORK = BOT / "work"                      # 날짜별 작업 폴더: research.json, drafts, covers, published.json
PROFILE = BOT / "browser-profile"        # Playwright 전용 로그인 프로필 (티스토리 세션 저장)
ARCHIVE_REPO = Path(os.environ.get("DB_ARCHIVE_REPO", HOME / "daily-bytes"))  # devSeodong/daily-bytes 클론
LAST30 = HOME / ".claude/skills/last30days/scripts/last30days.py"
LAST30_ENV = HOME / ".config/last30days/.env"
PY = os.environ.get("DB_PY", "/opt/homebrew/bin/python3.12")      # last30days 실행용 (시스템 python3.12)
BOT_PY = os.environ.get("DB_BOT_PY", str(BOT / "venv/bin/python"))  # 봇 스크립트/add_post.py용 venv (pillow, playwright, bs4)
BLOG = "https://dongseodong.tistory.com"

# 파일 번호 → 카테고리 정보
CATS = {
    "01-ai-issue":     {"slug": "ai-issue",  "label": "AI 이슈",   "head": "오늘의 AI 이슈",   "color": "#7C5CFF"},
    "02-ai-trend":     {"slug": "ai-trend",  "label": "AI 트렌드", "head": "오늘의 AI 트렌드", "color": "#10B981"},
    "03-cs-dev-issue": {"slug": "dev-issue", "label": "개발 이슈", "head": "오늘의 CS/개발 이슈", "color": "#F59E0B"},
}

# 비정기 심층 시리즈 (2026-11-28~): 초안 이름이 "ai-deep-"으로 시작하면 이 카테고리.
# 같은 날 여러 편을 올릴 수 있도록 키(파일 이름)는 글마다 달라요. 예: ai-deep-01-riemann
DEEP = {"slug": "ai-deep", "label": "AI 심층 분석", "head": "AI 심층 분석", "color": "#EC4899"}


def cat(key: str):
    """초안 키 → 카테고리 정보 (모르는 키면 None)."""
    if key in CATS:
        return CATS[key]
    if key.startswith("ai-deep-"):
        return DEEP
    return None

# 요일별 발행 (2026-11-27부터 하루 1편). datetime.weekday(): 월=0 ... 일=6. 일요일은 휴재.
SCHEDULE = {0: "01-ai-issue", 3: "01-ai-issue", 1: "03-cs-dev-issue", 4: "03-cs-dev-issue",
            2: "02-ai-trend", 5: "02-ai-trend"}


def todays_key(date: str):
    """그날 발행할 초안 키. 일요일이면 None."""
    import datetime as _dt
    return SCHEDULE.get(_dt.date.fromisoformat(date).weekday())


def day_dir(date: str) -> Path:
    d = WORK / date
    d.mkdir(parents=True, exist_ok=True)
    return d


def notify(title: str, msg: str):
    """맥 알림 + status 파일. 클라우드 쪽 AI가 status.json을 읽어 사용자에게 알려요."""
    import json, subprocess, time
    try:
        subprocess.run(["osascript", "-e", f'display notification {json.dumps(msg, ensure_ascii=False)} with title {json.dumps(title, ensure_ascii=False)} sound name "Glass"'], timeout=10)
    except Exception:
        pass
    st = BOT / "status.json"
    st.write_text(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "title": title, "msg": msg}, ensure_ascii=False, indent=2), encoding="utf-8")


def read_meta(html: str) -> dict:
    """초안 맨 위 <!-- 키: 값 --> 주석을 읽어요. 제목/태그(필수), 커버/슬러그(선택)."""
    import re
    meta = {}
    for k, v in re.findall(r"<!--\s*(제목|태그|커버|슬러그):\s*(.*?)\s*-->", html):
        meta[k] = v
    return meta


def strip_meta(html: str) -> str:
    import re
    return re.sub(r"<!--\s*(제목|태그|커버|슬러그):.*?-->\s*", "", html).strip()
