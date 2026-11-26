---
title: "맥 미니 한 대로 티스토리 매일 3편 자동 발행하기 (launchd + Playwright + Pillow)"
date: 2026-11-26
category: "AI 활용"
tistory: https://dongseodong.tistory.com/66
tags: ["티스토리자동화", "블로그자동화", "맥미니", "launchd", "Playwright", "Pillow", "파이썬", "ClaudeCode", "GitHub"]
cover: assets/2026-11-26-tistory-automation-mac-mini-batch.png
---
# 맥 미니 한 대로 티스토리 매일 3편 자동 발행하기 (launchd + Playwright + Pillow)

> 🧪 **AI 활용** · 2026-11-26 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/66)

![대표 이미지](assets/2026-11-26-tistory-automation-mac-mini-batch.png)

이 블로그에는 매일 저녁 8시쯤 **오늘의 AI 이슈** , **오늘의 AI 트렌드** , **오늘의 CS/개발 이슈** 세 편이 올라옵니다. 처음 며칠은 AI(Claude)가 브라우저를 직접 열어서 글을 쓰고, 에디터 버튼을 하나하나 눌러 발행까지 했습니다. 잘 돌아가긴 했는데, 글 한 편 올리는 데 쓰는 토큰의 상당 부분이 정작 글쓰기가 아니라 **화면 읽기와 클릭** 에 들어가고 있었습니다.

그래서 구조를 바꿨습니다. **글은 계속 AI가 직접 쓰고** , 그 앞뒤의 반복 작업(리서치 수집, 대표 이미지, 발행, 깃허브 보관)은 집에 있는 맥 미니가 파이썬 스크립트로 처리합니다. 이 글은 그 과정을 정리한 기록입니다. 코드는 전부 [daily-bytes 레포의 bot 폴더](https://github.com/devSeodong/daily-bytes/tree/main/bot)에 공개해 뒀습니다.

TL;DR · 한눈에 보기

1 글쓰기만 AI에게 남기고, 수집·이미지·발행·보관은 맥 미니의 파이썬 배치로 옮겼습니다.

2 도구는 launchd(예약 실행), Playwright(티스토리 에디터 자동 조작), Pillow(대표 이미지), pandoc(깃허브용 마크다운 변환)입니다.

3 같은 날 여러 번 돌려도 중복 발행이 안 되게 만들고, 실패하면 맥 알림과 상태 파일로 알려 줍니다.

목차

[1. 왜 배치로 바꿨나](#s1)

[2. 전체 구조 한눈에 보기](#s2)

[3. 리서치 수집: collect.py](#s3)

[4. 대표 이미지: thumb.py](#s4)

[5. 발행: publish.py (Playwright)](#s5)

[6. 깃허브 보관: archive.py](#s6)

[7. 예약 실행: launchd와 run.sh](#s7)

[8. 해 보고 느낀 점](#s8)

## 01 왜 배치로 바꿨나

**한 줄 요약:** AI가 잘하는 일(글쓰기)과 스크립트가 잘하는 일(정해진 클릭과 파일 처리)을 나눠서, 토큰은 글쓰기에만 쓰게 하기 위해서입니다.

### 처음 방식

처음에는 매일 정해진 시각에 AI 작업이 시작돼서, 리서치 결과 원문을 통째로 읽고, 글을 쓰고, 브라우저로 티스토리 에디터를 열어 제목·카테고리·태그를 채우고, 대표 이미지를 그려 붙이고, 발행 버튼까지 눌렀습니다. 발행한 글은 깃허브 레포에도 마크다운으로 보관했습니다.

문제는 브라우저 조작이었습니다. AI가 버튼 하나를 누르려면 화면을 읽고, 어디를 누를지 판단하고, 눌린 결과를 다시 확인해야 합니다. 매일 똑같은 순서로 반복되는 일인데도 매번 처음 보는 화면처럼 다뤄야 하니 비용이 계속 들었습니다.

### 바꾼 뒤

| 단계        | 처음                             | 지금                                                  |
|-------------|----------------------------------|-------------------------------------------------------|
| 리서치      | AI가 검색 결과 원문을 넓게 읽음  | `collect.py`가 상위 항목만 담은 작은 JSON을 만들어 둠 |
| 글쓰기      | AI                               | **AI (그대로)**                                       |
| 대표 이미지 | AI가 에디터 안에서 canvas로 그림 | `thumb.py` (Pillow)                                   |
| 발행        | AI가 브라우저 클릭               | `publish.py` (Playwright)                             |
| 깃허브 보관 | AI가 변환 후 push                | `archive.py`                                          |

💡 왜 중요할까

글쓰기를 템플릿으로 바꾸면 토큰은 더 줄겠지만, 매일 직접 꾸민 HTML 글이 이 블로그의 핵심이라 그건 남겨 뒀습니다. "무엇을 자동화할지"보다 "무엇을 자동화하지 않을지"를 먼저 정한 게 이번 작업에서 제일 중요했습니다.

## 02 전체 구조 한눈에 보기

**한 줄 요약:** 19:00에 맥 미니가 자료를 모으고, AI가 그걸 읽어 글을 쓴 뒤 발행 스크립트를 부르고, 20:40에는 혹시 빠진 글만 올리는 예비 실행이 돕니다.

| 시각 (KST)   | 하는 일                                        | 담당                              |
|--------------|------------------------------------------------|-----------------------------------|
| 19:00        | 리서치 수집 → `research.json`                  | launchd → `run.sh collect`        |
| 19:21~       | research.json을 읽고 3편 HTML 작성 → `drafts/` | AI (예약 작업)                    |
| 글 작성 직후 | 대표 이미지 → 발행 → 깃허브 보관               | AI가 `run.sh publish public` 호출 |
| 20:40        | 예비 발행 (이미 올린 글은 건너뜀)              | launchd                           |

STEP 1 · 수집

last30days, Brave 뉴스, GitHub 검색 결과 중 상위 항목만 JSON 한 파일로

STEP 2 · 글쓰기

AI가 JSON과 꼭 필요한 원문 몇 개만 읽고 HTML 3편 작성

STEP 3 · 이미지

초안 맨 위 주석의 문구로 1200×630 대표 이미지 생성

STEP 4 · 발행·보관

Playwright로 공개 발행, 이어서 마크다운으로 깃허브 push

글쓰기 단계는 Claude의 예약 작업이 매일 19:21에 시작해서, Remote Control로 맥 미니에 접속해 진행합니다. 맥 미니 안에서 `research.json`을 읽고, 초안을 `drafts/`에 저장한 뒤, 같은 자리에서 발행 스크립트를 부르는 데까지가 AI의 몫입니다. 발행이 끝나면 `published.json`과 로그를 읽어서 세 편의 주소를 확인합니다.

모든 단계는 날짜별 작업 폴더 하나를 주고받습니다. 단계끼리 약속한 건 파일 이름뿐이라, 한 단계만 따로 다시 돌리기도 쉽습니다.

▶ 날짜별 작업 폴더 구조

```
~/daily-bytes-bot/
├── venv/                  # 봇 전용 파이썬 가상환경
├── browser-profile/       # Playwright 전용 로그인 프로필
├── logs/2026-11-27.log
├── status.json            # 마지막 알림 (실패, 로그인 만료 등)
└── work/2026-11-27/
    ├── research.json      # 19:00 수집 결과
    ├── drafts/            # AI가 쓴 글
    │   ├── 01-ai-issue.html
    │   ├── 02-ai-trend.html
    │   └── 03-cs-dev-issue.html
    ├── covers/            # 대표 이미지
    └── published.json     # 발행된 글 주소
```

## 03 리서치 수집: collect.py

**한 줄 요약:** 세 가지 출처를 돌려서 카테고리별 상위 항목만 남긴 작은 JSON을 만들고, AI는 이 파일 하나만 읽습니다.

### 세 가지 출처

| 출처            | 쓰는 곳            | 메모                                                                                           |
|-----------------|--------------------|------------------------------------------------------------------------------------------------|
| last30days      | 세 카테고리 전부   | 여러 커뮤니티를 한 번에 훑는 리서치 스킬. `--days 7 --store`로 최근 일주일만, 결과는 누적 저장 |
| Brave 뉴스 API  | AI 이슈, 개발 이슈 | 최근 일주일(`freshness=pw`) 뉴스 상위 8개                                                      |
| GitHub 검색 API | AI 트렌드          | 최근 7일 안에 만들어진 llm, ai-agent, mcp 등 토픽 레포를 스타 순으로                           |

GitHub 쪽은 따로 키 없이 검색 API를 그대로 씁니다. "최근에 생긴 레포 중 스타가 빨리 붙는 것"이 AI 트렌드 글의 재료라서, `created:>=날짜` 조건이 핵심입니다.

▶ 최근 N일 안에 생긴 AI 레포를 스타 순으로 (collect.py 일부)

```
since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
for topic in ["llm", "ai-agent", "machine-learning", "mcp"]:
    q = f"topic:{topic} created:>={since}"
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": 10})
    for r in get_json(url).get("items", []):
        out.append({"repo": r["full_name"], "stars": r["stargazers_count"],
                    "created": r["created_at"][:10], "desc": (r.get("description") or "")[:200]})
```

### 막혔던 곳: 스크립트 안에서 돌린 last30days가 멈춤

터미널에서는 잘 되던 last30days가 배치 안에서는 수집을 시작하지도 않고 끝났습니다. 원인은 환경변수였습니다. AI 작업 세션에서 스크립트를 부르면 `CLAUDE`로 시작하는 환경변수가 따라 들어오는데, last30days는 이걸 보고 "에이전트가 실행 중이니 계획(--plan)을 먼저 넘겨라"라는 모드로 동작했습니다. 그래서 하위 프로세스에 넘길 때 이 변수들을 지우고, 수집만 하는 `--research-only` 옵션을 붙였습니다.

▶ 하위 프로세스에 넘길 환경변수 정리 (collect.py 일부)

```
def load_env():
    # CLAUDE로 시작하는 변수가 있으면 last30days가 수집 전에 멈춰서 지움
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    # API 키는 맥 미니의 .env 파일에서만 읽음 (코드와 레포에는 없음)
    for line in LAST30_ENV.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env.setdefault(k.strip(), v.strip().strip('"'))
    return env
```

⚠ 키는 맥 미니에만

API 키는 맥 미니의 설정 파일에만 두고, 코드와 깃허브 레포, AI와의 대화에는 넣지 않았습니다. 키가 비어 있으면 그 출처만 건너뛰고 `research.json`의 `warnings`에 이유를 남깁니다. 실제로 처음 돌렸을 때는 키가 비어 있어서 Hacker News와 GitHub 결과만 모였고, 이 경고 덕분에 바로 알아챘습니다.

첫 실제 실행은 38초 걸렸고, 결과 파일은 35KB였습니다. AI가 매일 읽는 양이 이 정도로 줄어든 것입니다.

## 04 대표 이미지: thumb.py

**한 줄 요약:** 픽셀 그리드 틀은 고정하고 제목만 바꿔 Pillow로 1200×630 PNG를 그립니다.

예전에는 AI가 에디터 페이지 안에서 `<canvas>`로 이미지를 그리고 붙여 넣었습니다. 이제는 같은 디자인을 Pillow로 옮겨서, 카테고리마다 색과 머리글만 바꿔 줍니다.

| 카테고리  | 색         | 머리글              |
|-----------|------------|---------------------|
| AI 이슈   | ■ \#7C5CFF | 오늘의 AI 이슈      |
| AI 트렌드 | ■ \#10B981 | 오늘의 AI 트렌드    |
| 개발 이슈 | ■ \#F59E0B | 오늘의 CS/개발 이슈 |

이미지에 들어갈 문구는 AI가 초안 맨 위에 주석으로 적어 둡니다. 발행 스크립트도 같은 주석에서 제목과 태그를 읽기 때문에, AI와 스크립트 사이의 약속은 이 몇 줄이 전부입니다.

▶ 초안 맨 위 주석 (AI가 쓰고, 스크립트가 읽음)

```
<!-- 제목: 오늘의 AI 이슈 (2026.11.27) - ... -->
<!-- 태그: AI뉴스,OpenAI,... -->
<!-- 커버: 첫 줄 | 둘째 줄 | 셋째 줄 -->
<!-- 슬러그: openai-gpt-launch -->
```

오른쪽 위의 은은한 빛은 카테고리 색으로 칠한 원 두 개를 가우시안 블러로 흐린 마스크를 만들고, 배경과 합성해서 만들었습니다.

▶ 카테고리 색 빛 번짐 (thumb.py 일부)

```
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.ellipse((780, 30, 1160, 410), fill=150)
md.ellipse((880, 130, 1060, 310), fill=235)      # 가운데가 더 밝게
mask = mask.filter(ImageFilter.GaussianBlur(85))
tint = Image.new("RGB", (W, H), tuple(int(BG[i] * 0.35 + col[i] * 0.65) for i in range(3)))
img = Image.composite(tint, img, mask)
```

글꼴은 기존 이미지와 같은 Noto Sans KR을 맥 미니에 설치해서 맞췄습니다. 없으면 macOS 기본 글꼴인 Apple SD Gothic Neo로 대신 그립니다. 초안이 바뀌지 않았으면 이미 만든 이미지를 그대로 재사용합니다.

## 05 발행: publish.py (Playwright)

**한 줄 요약:** 티스토리는 Open API가 종료돼서, Playwright로 실제 글쓰기 화면을 조작해 발행합니다.

### 로그인은 한 번만

Playwright의 `launch_persistent_context`를 쓰면 브라우저 프로필 폴더에 로그인 세션이 남습니다. 처음 한 번만 카카오 QR 로그인을 하고(로그인 상태 유지 체크), 그다음부터는 저장된 세션으로 바로 관리 화면에 들어갑니다. 비밀번호는 스크립트에 넣지 않았습니다.

▶ 로그인 세션을 저장하는 전용 브라우저 (publish.py 일부)

```
ctx = p.chromium.launch_persistent_context(
    str(PROFILE), headless=False, locale="ko-KR",
    viewport={"width": 1400, "height": 1000})
page = ctx.pages[0] if ctx.pages else ctx.new_page()
# "작성 중인 글이 있어요, 이어서 쓸까요?" 창은 닫고 새로 쓰기
page.on("dialog", lambda d: d.dismiss())
```

### 본문과 대표 이미지 넣기

티스토리 에디터는 TinyMCE 기반이라, 직접 꾸민 HTML을 `setContent`로 한 번에 넣으면 인라인 스타일이 그대로 살아남습니다. 대표 이미지는 파일 선택 창을 거치지 않고, 이미지 파일을 담은 붙여넣기(paste) 이벤트를 본문 맨 위에 보내서 티스토리가 직접 업로드하게 했습니다.

▶ 이미지 파일 붙여넣기로 업로드 (page.evaluate 안에서 실행)

```
const e = tinymce.activeEditor, body = e.getBody();
const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const file = new File([bin], 'cover.png', {type: 'image/png'});
const p = e.dom.create('p', {}, '<br>');
body.insertBefore(p, body.firstChild);          // 맨 위에 빈 줄
e.selection.setCursorLocation(p, 0); e.focus();
const dt = new DataTransfer(); dt.items.add(file);
body.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
```

### 막혔던 곳 두 가지

| 증상                         | 원인                                                                                         | 해결                                                                |
|------------------------------|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 로그인 안 됐는데 "로그인 OK" | 비로그인이면 관리 페이지가 조금 늦게 JS로 로그인 화면으로 넘어감. 그 전에 주소만 보고 판단함 | `networkidle`까지 기다린 뒤 관리 화면 링크가 실제로 있는지까지 확인 |
| 공개 범위 클릭이 안 먹음     | 라디오 input과 label의 높이가 0이라 클릭 대상이 안 됨                                        | label 안쪽 글자(span)를 누르고, `is_checked`로 선택됐는지 다시 확인 |

▶ 공개 범위 선택 후 확인 (publish.py 일부)

```
VIS = {"public": "#open20", "protected": "#open15", "private": "#open0"}
page.click("#publish-layer-btn")
page.wait_for_selector(VIS[vis], state="attached", timeout=10000)
page.click(f"label[for={VIS[vis][1:]}] .checkbox-text")
if not page.is_checked(VIS[vis]):
    raise RuntimeError(f"공개 범위 {vis} 선택 실패")
```

📌 비공개로 먼저 테스트

에디터의 선택자들은 처음엔 추측이었습니다. 그래서 공개 발행 전에 **비공개 글 1편** 을 올려서 카테고리, 태그, 인라인 스타일, 대표 이미지가 전부 의도대로 들어갔는지 확인한 뒤에 공개 배치로 넘어갔습니다.

## 06 깃허브 보관: archive.py

**한 줄 요약:** 공개 발행된 글만 마크다운으로 바꿔 [daily-bytes](https://github.com/devSeodong/daily-bytes) 레포에 쌓고, README의 최근 글 목록도 다시 만듭니다.

발행 스크립트가 남긴 `published.json`(제목, 태그, 주소, 공개 범위)을 읽고, 레포 안의 `scripts/add_post.py`를 부릅니다. 이 스크립트는 BeautifulSoup으로 스타일과 이미지를 걷어 낸 뒤 pandoc으로 GitHub 마크다운을 만듭니다. 파일은 `카테고리/연/월/날짜-슬러그.md`로 저장됩니다.

▶ add_post.py를 직접 쓸 때

```
python3 scripts/add_post.py \
  --category ai-issue --date 2026-11-27 --slug example-slug \
  --title "오늘의 AI 이슈 (2026.11.27) - ..." \
  --url https://dongseodong.tistory.com/00 \
  --tags "AI뉴스,예시" \
  --html post.html --cover cover.png
```

그날 그 카테고리의 파일이 이미 있으면 건너뛰고, 커밋할 게 없으면 조용히 끝납니다. 비공개 테스트 글은 보관하지 않습니다.

## 07 예약 실행: launchd와 run.sh

**한 줄 요약:** macOS 기본 예약 도구인 launchd가 정해진 시각에 `run.sh`를 부르고, run.sh가 중복 실행과 실패를 관리합니다.

### launchd 등록

cron 대신 launchd를 쓴 이유는 로그인한 화면 세션(Aqua)에서 실행되게 지정할 수 있어서입니다. Playwright가 화면이 있는 브라우저를 띄우기 때문에 이게 필요했습니다.

▶ ~/Library/LaunchAgents/com.dailybytes.collect.plist

```
<dict>
  <key>Label</key><string>com.dailybytes.collect</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>/Users/me/daily-bytes-src/bot/run.sh</string><string>collect</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
  <key>LimitLoadToSessionType</key><string>Aqua</string>
</dict>
```

▶ 등록하고 확인하기

```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.dailybytes.collect.plist
launchctl list | grep dailybytes                          # 등록 확인
launchctl kickstart -k gui/$(id -u)/com.dailybytes.collect   # 지금 한 번 시험 실행
```

### 여러 번 돌려도 안전하게

발행은 AI가 한 번 부르고, 20:40에 launchd가 한 번 더 부릅니다. 그래서 run.sh는 **같은 작업이 겹치지 않게 잠금 폴더** 를 만들고, 발행이 실패하면 보관을 건너뜁니다. 공개 배치 시작일 전에는 공개 발행을 하지 않는 안전장치도 넣었습니다.

▶ 잠금과 실패 처리 (run.sh 일부)

```
LOCK="$HOME/daily-bytes-bot/.lock-${1:-x}"
if ! mkdir "$LOCK" 2>/dev/null; then
  # 1시간 넘게 남은 잠금은 비정상 종료로 보고 지움
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +60)" ]; then rm -rf "$LOCK"; mkdir "$LOCK"
  else echo "다른 실행 중이라 종료"; exit 0; fi
fi
trap 'rm -rf "$LOCK"' EXIT

"$PY" thumb.py --date "$DATE" && "$PY" publish.py --date "$DATE" --visibility "$VIS"; rc=$?
if [ $rc -eq 0 ]; then "$PY" archive.py --date "$DATE"; rc=$?
else echo "발행 실패(rc=$rc) → 보관 건너뜀"; fi
```

`mkdir`는 폴더가 이미 있으면 실패하고, 만드는 동작이 한 번에 일어나서 간단한 잠금으로 쓰기 좋습니다. 발행 스크립트도 `published.json`에 이미 있는 글은 건너뛰기 때문에, 두 번째 실행은 빠진 글만 올립니다.

🔥 실패는 조용히 넘기지 않기

로그인이 풀리거나 발행이 실패하면 맥 알림을 띄우고 `status.json`에 이유를 적습니다. 매일 글을 쓰는 AI 작업이 이 파일을 읽어서 무엇이 실패했는지 알려 줍니다. 자동화에서 가장 무서운 건 실패가 아니라 실패를 모르고 지나가는 거라서, 이 부분을 제일 먼저 만들었습니다.

## 08 해 보고 느낀 점

**한 줄 요약:** 사람이 매일 하던 순서를 그대로 코드로 옮기되, 단계 사이를 파일로 끊어 두니 고치기도 확인하기도 쉬웠습니다.

| 잘 된 점                                                    | 아직 남은 것                                             |
|-------------------------------------------------------------|----------------------------------------------------------|
| 단계마다 입력과 출력이 파일이라, 한 단계만 다시 돌리기 쉬움 | Brave 등 일부 API 키를 채워야 뉴스 수집이 더 풍부해짐    |
| AI는 글쓰기와 결과 확인만 해서 하는 일이 단순해짐           | 알림이 아직 맥 알림과 상태 파일뿐 (휴대폰 알림은 미연결) |
| 비공개 테스트 → 공개 전환 순서로 위험 없이 바꿈             | 티스토리 에디터 화면이 바뀌면 선택자를 다시 맞춰야 함    |

> 자동화할 것보다, 사람이(또는 AI가) 계속 직접 할 것을 먼저 정하기

## 정리

**핵심 1.** 매일 반복되는 클릭과 파일 처리는 스크립트로, 판단이 필요한 글쓰기는 AI로 나눴습니다.

**핵심 2.** launchd(예약) + Playwright(발행) + Pillow(이미지) + pandoc(보관) 조합이면 맥 미니 한 대로 충분합니다.

**핵심 3.** 잠금, 이미 한 일 건너뛰기, 실패 알림을 넣어 두면 같은 날 몇 번을 돌려도 안전합니다.

✦ 지금 해볼 것

☐ 내 블로그 작업 중 매일 똑같이 반복되는 단계 적어 보기

☐ 그중 하나를 Playwright로 비공개 테스트 발행까지 해 보기

☐ launchd 예약을 하나 등록하고 `launchctl kickstart`로 시험 실행하기

## 자주 묻는 질문

### 티스토리는 API로 글을 올릴 수 없습니까?

티스토리 Open API는 종료돼서 지금은 API로 글을 올릴 수 없습니다. 그래서 이 배치는 Playwright로 실제 글쓰기 화면(`/manage/newpost`)을 열어 제목, 카테고리, 본문, 태그, 공개 범위, 대표 이미지를 채우고 발행 버튼을 누릅니다.

### 맥 미니가 꺼져 있으면 어떻게 됩니까?

launchd 작업은 맥이 켜져 있고 로그인된 화면 세션이 있을 때만 돕니다. 그래서 맥 미니는 항상 켜 두고 있고, 발행이 실패하면 맥 알림과 `status.json`으로 남겨서 그날 AI 작업이 알려 줍니다. 20:40 예비 실행이 빠진 글만 다시 올리는 것도 같은 이유입니다.

### 로그인 세션이 풀리면 어떻게 됩니까?

발행 전에 관리 화면에 실제로 들어가지는지부터 확인하고, 풀렸으면 발행을 멈추고 "로그인 만료" 알림을 남깁니다. 다시 로그인할 때는 `publish.py --login`이 카카오 QR 화면을 띄우고, 카카오톡으로 스캔하면 세션이 다시 저장됩니다.

## 참고 링크

[daily-bytes · bot 폴더 (이 글의 코드) ↗](https://github.com/devSeodong/daily-bytes/tree/main/bot)[Playwright · launch_persistent_context ↗](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context)[Pillow 문서 ↗](https://pillow.readthedocs.io/)[pandoc ↗](https://pandoc.org/)

---

`#티스토리자동화` `#블로그자동화` `#맥미니` `#launchd` `#Playwright` `#Pillow` `#파이썬` `#ClaudeCode` `#GitHub`
