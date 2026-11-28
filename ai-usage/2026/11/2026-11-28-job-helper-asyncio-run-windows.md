---
title: "윈도우에서만 터진 asyncio.run 오류 (FastAPI)"
date: 2026-11-28
category: "AI 활용"
tistory: https://dongseodong.tistory.com/78
tags: ["파이썬", "asyncio", "FastAPI", "이벤트루프", "WindowsOCR", "WinRT", "스레드풀", "취업도우미에이전트", "AI활용"]
cover: assets/2026-11-28-job-helper-asyncio-run-windows.png
---
# 윈도우에서만 터진 asyncio.run 오류 (FastAPI)

> 🧪 **AI 활용** · 2026-11-28 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/78)

![대표 이미지](assets/2026-11-28-job-helper-asyncio-run-windows.png)

**사진을 끌어다 넣으면 윈도우에서만 글자 인식이 멈추던 버그의 원인(이벤트 루프 안의 asyncio.run)과 해결 방법을 정리한 글입니다.**

이 글 한눈에 보기

1 **증상:** 앱 화면에 사진을 넣으면 글자 인식이 에러로 멈췄습니다. 맥·리눅스에서는 재현되지 않았습니다.

2 **원인:** 이미 이벤트 루프가 돌고 있는 FastAPI async 라우트 안에서, Windows OCR 코드가 `asyncio.run`을 또 불렀습니다.

3 **해결:** OCR을 이벤트 루프 밖 스레드에서 돌리고, 업로드 후 읽기도 스레드풀에서 실행했습니다.

📚 취업 도우미 에이전트 개발기 시리즈

1편 · 기획 [왜 만들었고, 화면과 문서를 어떻게 준비했나](https://dongseodong.tistory.com/73)

2편 · 설계 [로컬 앱 구조, 토큰 예산, 15인 심사, 개인정보 규칙](https://dongseodong.tistory.com/74)

3편 · 개발 [PR 12개로 돌아본 이틀과 막혔던 부분](https://dongseodong.tistory.com/75)

단독① [토큰 절약 vs 누락 0](https://dongseodong.tistory.com/76)

단독② [스택 PR이 main에 안 들어간 이유](https://dongseodong.tistory.com/77)

단독③ **윈도우에서만 터진 asyncio.run 오류** 지금 읽는 글

단독④ [맥에서 Windows 한국어 OCR 테스트하기](https://dongseodong.tistory.com/79)

단독⑤ [앱에서 AI 구독을 쓰는 방법: 공식 CLI 호출](https://dongseodong.tistory.com/80)

목차

[1. 증상: 윈도우에서만 멈추는 사진 넣기](#s1)

[2. 원인: 돌고 있는 루프 안에서 루프를 또 만들기](#s2)

[3. 해결: OCR은 루프 밖 스레드에서](#s3)

[4. 교훈: 실제 사용 환경에서 테스트하기](#s4)

## 01 증상: 윈도우에서만 멈추는 사진 넣기

**한 줄 요약:** 같은 코드가 맥과 리눅스에서는 통과하고 윈도우에서만 실패했습니다.

[3편](https://dongseodong.tistory.com/75)에서 소개한 「바로 넣기」 기능은 앱 화면에 사진을 끌어다 놓으면 취업 폴더에 저장하고 바로 글자를 읽는 기능입니다. 그런데 윈도우에서 사진을 넣자 글자 인식 단계에서 에러가 나며 멈췄습니다.

| 환경       | OCR 엔진                             | 결과     |
|------------|--------------------------------------|----------|
| Windows    | Windows 내장 OCR (WinRT, 비동기 API) | **실패** |
| macOS      | macOS 내장 Vision (동기 호출)        | 통과     |
| Linux (CI) | OCR 없음 (건너뜀)                    | 통과     |

표를 보면 이유가 어느 정도 보입니다. 문제가 된 코드 경로는 **윈도우에서만 실행되는 경로** 였습니다.

## 02 원인: 돌고 있는 루프 안에서 루프를 또 만들기

**한 줄 요약:** `asyncio.run`은 새 이벤트 루프를 만드는 함수라서, 이미 루프가 도는 곳에서 부르면 에러가 납니다.

### FastAPI의 async 라우트는 이벤트 루프 위에서 돕니다

FastAPI에서 `async def`로 만든 라우트는 서버(uvicorn)의 이벤트 루프 안에서 실행됩니다. 사진 업로드 라우트도 파일을 받기 위해 `async def`였습니다.

### Windows OCR은 비동기 API입니다

Windows 내장 OCR(`Windows.Media.Ocr`)은 WinRT의 비동기 API라서, 파이썬에서 부르려면 await가 필요합니다. 처음 코드는 OCR 함수를 "보통 함수처럼" 쓰기 위해 안에서 `asyncio.run`으로 감싸 두었습니다.

▶ 문제가 된 구조 (설명용 예시)

```
import asyncio

def ocr_image(path: str) -> str:
    # 단독으로 부를 때는 문제없습니다 (테스트, 명령줄 실행 등)
    return asyncio.run(_ocr_winrt(path))     # 새 이벤트 루프를 만듦

@app.post("/quick/photo")
async def upload_photo(file: UploadFile):     # 이미 이벤트 루프 안
    saved = await save_to_folder(file)
    text = ocr_image(saved)                    # 여기서 asyncio.run 호출 → 에러
    return {"text": text}
```

▶ 이때 나는 에러

```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

맥의 Vision 호출은 동기 함수라 `asyncio.run`을 거치지 않고, 리눅스는 OCR을 건너뛰기 때문에 이 경로를 아예 밟지 않습니다. 그래서 개발 중이던 맥과 리눅스 CI에서는 보이지 않았던 것입니다.

💡 단독으로 부를 때는 멀쩡한 이유

OCR 함수를 테스트나 명령줄에서 단독으로 부르면 돌고 있는 루프가 없으니 `asyncio.run`이 정상 동작합니다. 문제는 "async 라우트 안에서 부를 때"만 생기는 조합이라, 함수 자체만 보면 이상한 곳이 없어 보입니다.

## 03 해결: OCR은 루프 밖 스레드에서

**한 줄 요약:** 무거운 동기 작업과 별도 루프가 필요한 작업은 스레드로 보내고, 라우트는 그 결과를 await합니다.

해결은 두 가지였습니다. OCR 함수는 자기만의 루프를 가진 별도 스레드에서 실행되게 하고, 업로드 후 파일을 읽어 정제하는 작업은 스레드풀에서 돌렸습니다.

▶ 고친 구조 (설명용 예시)

```
import asyncio
from starlette.concurrency import run_in_threadpool

def ocr_image(path: str) -> str:
    """어디서 불러도 안전하게: 돌고 있는 루프가 있으면 새 스레드에서 실행합니다."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:                       # 루프 없음 → 그대로 실행
        return asyncio.run(_ocr_winrt(path))
    # 루프 안 → 별도 스레드에서 새 루프로 실행
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(lambda: asyncio.run(_ocr_winrt(path))).result()

@app.post("/quick/photo")
async def upload_photo(file: UploadFile):
    saved = await save_to_folder(file)
    # 오래 걸리는 동기 작업은 스레드풀로 → 이벤트 루프가 막히지 않음
    text = await run_in_threadpool(ocr_image, saved)
    return {"text": text}
```

| 방법                                      | 언제 쓰나                                                               |
|-------------------------------------------|-------------------------------------------------------------------------|
| `await`로 바로 호출                       | 호출하는 쪽도 async이고, 대상이 진짜 비동기 함수일 때                   |
| `asyncio.to_thread` / `run_in_threadpool` | 오래 걸리는 동기 함수(OCR, 파일 파싱)를 async 라우트에서 부를 때        |
| 새 스레드 + `asyncio.run`                 | 동기 함수 안에서 비동기 API를 써야 하고, 호출 위치를 예측하기 어려울 때 |

📌 FastAPI의 동기 라우트

라우트를 `async def`가 아니라 `def`로 만들면 FastAPI가 알아서 스레드풀에서 실행해 줍니다. 다만 이 앱의 업로드 라우트는 파일을 await로 받기 때문에 async를 유지하고, 무거운 부분만 스레드풀로 보냈습니다.

## 04 교훈: 실제 사용 환경에서 테스트하기

**한 줄 요약:** 윈도우 CI를 굳이 붙여 둔 덕분에, 사용자가 겪기 전에 이 버그를 잡았습니다.

개발은 맥에서 하고 실제 사용자는 윈도우를 씁니다. [2편](https://dongseodong.tistory.com/74)에서 정한 대로 GitHub Actions에서 Windows·macOS·Linux 세 OS로 테스트를 돌리고 있었기 때문에, 이 버그는 사용자 PC가 아니라 CI에서 먼저 드러났습니다.

✦ 지금 해볼 것

☐ OS마다 다른 코드 경로가 있다면, 그 경로를 실제로 밟는 테스트가 그 OS에서 도는지 확인

☐ 라이브러리 함수 단위 테스트뿐 아니라, 웹 라우트를 통과하는 테스트도 함께 두기

☐ async 라우트 안에서 `asyncio.run`, `time.sleep`, 무거운 동기 호출이 없는지 검색해 보기

▶ async 함수 안의 위험한 호출 찾기

```
grep -rn "asyncio.run(" app/ | grep -v tests/
grep -rn "time.sleep(" app/
```

## 정리

**핵심 1.** `asyncio.run`은 새 루프를 만드는 함수라서, FastAPI async 라우트처럼 이미 루프가 도는 곳에서 부르면 RuntimeError가 납니다.

**핵심 2.** 윈도우 OCR만 비동기 API라서 이 경로가 윈도우에서만 실행됐고, 맥·리눅스에서는 보이지 않았습니다.

**핵심 3.** OCR은 별도 스레드에서, 무거운 작업은 스레드풀에서 실행해 해결했고, 윈도우 CI가 이 버그를 먼저 잡았습니다.

## 자주 묻는 질문

### "asyncio.run() cannot be called from a running event loop" 에러는 왜 납니까?

`asyncio.run`은 새 이벤트 루프를 만들어 실행하는 함수인데, 이미 이벤트 루프가 돌고 있는 곳(FastAPI async 라우트, Jupyter 등)에서 부르면 루프를 겹쳐 만들 수 없어 이 에러가 납니다. 호출하는 쪽이 async라면 await로 부르고, 동기 함수라면 별도 스레드에서 실행하는 방식으로 해결합니다.

### FastAPI async 라우트에서 오래 걸리는 동기 함수는 어떻게 부릅니까?

`await asyncio.to_thread(함수, 인자)`나 Starlette의 `await run_in_threadpool(함수, 인자)`로 스레드에서 실행하면 이벤트 루프가 막히지 않습니다. 라우트 전체가 동기 작업이라면 `def`로 선언해 FastAPI가 스레드풀에서 돌리게 할 수도 있습니다.

### 왜 윈도우에서만 이 문제가 생겼습니까?

이 앱은 윈도우에서는 비동기 API인 Windows 내장 OCR을, 맥에서는 동기 호출인 Vision을 쓰고, 리눅스에서는 OCR을 건너뜁니다. 그래서 asyncio.run을 거치는 코드 경로가 윈도우에서만 실행됐습니다.

## 참고 링크

[Python Docs · asyncio.run ↗](https://docs.python.org/3/library/asyncio-runner.html)[Python Docs · asyncio.to_thread ↗](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)[FastAPI Docs · Concurrency and async ↗](https://fastapi.tiangolo.com/async/)[Microsoft Learn · Windows.Media.Ocr ↗](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr)

---

`#파이썬` `#asyncio` `#FastAPI` `#이벤트루프` `#WindowsOCR` `#WinRT` `#스레드풀` `#취업도우미에이전트` `#AI활용`
