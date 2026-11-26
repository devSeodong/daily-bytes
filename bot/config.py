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
PY = os.environ.get("DB_PY", "/opt/homebrew/bin/python3.12")
BLOG = "https://dongseodong.tistory.com"

# 파일 번호 → 카테고리 정보
CATS = {
    "01-ai-issue":     {"slug": "ai-issue",  "label": "AI 이슈",   "head": "오늘의 AI 이슈",   "color": "#7C5CFF"},
    "02-ai-trend":     {"slug": "ai-trend",  "label": "AI 트렌드", "head": "오늘의 AI 트렌드", "color": "#10B981"},
    "03-cs-dev-issue": {"slug": "dev-issue", "label": "개발 이슈", "head": "오늘의 개발 이슈", "color": "#F59E0B"},
}


def day_dir(date: str) -> Path:
    d = WORK / date
    d.mkdir(parents=True, exist_ok=True)
    return d


def notify(title: str, msg: str):
    """맥 알림 + status 파일. 클라우드 쪽 AI가 status.json을 읽어 사용자에게 알려요."""
    import json, subprocess, time
    try:
        subprocess.run(["osascript", "-e", f'display notification {json.dumps(msg)} with title {json.dumps(title)} sound name "Glass"'], timeout=10)
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
