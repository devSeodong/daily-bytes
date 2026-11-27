# daily-bytes bot (맥 미니 배치)

매일 오늘의 IT 3편을 만드는 과정 중 **글쓰기(AI가 HTML 작성)를 뺀 나머지**를 맥 미니에서 돌리는 스크립트예요.

| 시각 (KST) | 단계 | 담당 |
|---|---|---|
| 19:00 | `collect.py` 리서치 수집 → `work/<날짜>/research.json` | launchd |
| 19:21 | research.json 읽고 그날 1편 HTML 작성 → `work/<날짜>/drafts/0N-*.html` | AI |
| 20:00 | `thumb.py` 대표 이미지 → `publish.py` 발행 → `archive.py` 깃허브 보관 | launchd |

## 요일제 (2026-11-27부터 하루 1편)
월·목 `01-ai-issue` / 화·금 `03-cs-dev-issue` / 수·토 `02-ai-trend` / 일요일 휴재. `config.SCHEDULE`에서 바꿀 수 있어요. 수집·발행 모두 그날 카테고리 하나만 처리하고, 일요일엔 `run.sh`가 바로 끝나요. 요일과 상관없이 돌리려면 `collect.py --all`, `publish.py --all`.

## 초안 파일 규칙
`drafts/01-ai-issue.html`, `02-ai-trend.html`, `03-cs-dev-issue.html`. 맨 위 주석:
```html
<!-- 제목: 오늘의 AI 이슈 (2026.11.26) - ... -->
<!-- 태그: AI뉴스,OpenAI,... -->
<!-- 커버: 첫 줄 | 둘째 줄 | 셋째 줄 -->   (선택)
<!-- 슬러그: openai-gpt-6-launch -->      (선택, 깃허브 파일 이름)
```

## 설치 (한 번)
```bash
git clone -b claude/project-thread-hke4hx https://github.com/devSeodong/daily-bytes ~/daily-bytes-src
ln -s ~/daily-bytes-src/bot ~/daily-bytes-bot/code   # 또는 복사
/opt/homebrew/bin/python3.12 -m pip install -r requirements.txt
/opt/homebrew/bin/python3.12 -m playwright install chromium
gh auth setup-git
python3.12 publish.py --login        # 카카오 QR 로그인 (한 번)
```
launchd: `launchd/*.plist`의 `__BOT_DIR__`, `__VIS__`(public|private)를 바꿔 `~/Library/LaunchAgents/`에 넣고 `launchctl load`.

## 알림
로그인 쿠키는 `~/daily-bytes-bot/state.json`(권한 600)에도 백업돼서 브라우저를 다시 켜도 되살아나요. 로그인할 땐 QR 탭을 열기 전에 "로그인 상태 유지"를 체크해요.

실패/로그인 만료 시 맥 알림 + `~/daily-bytes-bot/status.json`. 로그는 `~/daily-bytes-bot/logs/<날짜>.log`.
