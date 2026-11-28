---
title: "오늘의 AI 트렌드 (2026.11.28) - 에이전트에게 도구를 쥐여 주는 레포들: safe-anything, fast-anything, agent-sim"
date: 2026-11-28
category: "AI 트렌드"
tistory: https://dongseodong.tistory.com/86
tags: ["AI트렌드", "깃허브트렌드", "safe-anything", "fast-anything", "agent-sim", "MCP", "러스트", "코딩에이전트", "iOS시뮬레이터", "오픈소스"]
cover: assets/2026-11-28-agent-native-rust-tools-and-ios-simulator.png
---
# 오늘의 AI 트렌드 (2026.11.28) - 에이전트에게 도구를 쥐여 주는 레포들: safe-anything, fast-anything, agent-sim

> 📈 **AI 트렌드** · 2026-11-28 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/86)

![대표 이미지](assets/2026-11-28-agent-native-rust-tools-and-ios-simulator.png)

이번 주 GitHub에서 빠르게 별이 붙은 신규 레포에는 한 가지 공통점이 있습니다. 사람이 쓰는 도구가 아니라 **에이전트가 직접 실행하는 도구** 라는 점입니다. 취약점을 찾는 스캐너, 느린 코드만 골라 다시 쓰는 도구, 그리고 맥 없이 iOS 앱을 조작하게 해 주는 시뮬레이터입니다. 세 개 모두 Rust로 쓰인 CLI이면서 동시에 MCP 서버로 붙습니다. 별 수는 2026년 11월 28일 저녁 GitHub API 기준이고, 기능과 수치는 각 레포의 README에 적힌 내용입니다.

TL;DR · 한눈에 보기

1 **safe-anything** (별 843): 72개 규칙으로 XSS·SQL 인젝션·유출된 키·의존성 CVE를 찾습니다. **에이전트 설정 자체** (MCP 서버, 스킬, 훅)도 검사 대상입니다.

2 **fast-anything** (별 4,574): "느린 5%만 다시 쓴다"는 접근입니다. README의 파이썬 중복 제거 예시에서 **4.91초가 42밀리초** 로 줄었습니다.

3 **shrink-anything** (별 410): 테스트를 통과시킨 채로 코드를 줄입니다. 데모 앱 기준 **읽어야 할 토큰이 46% 감소** 했다고 적혀 있습니다.

4 **agent-sim** (별 631): 맥 없이 x86-64 리눅스에서 애플 iOS 시뮬레이터 런타임을 돌립니다. 화면을 **텍스트로 읽고** 탭·입력까지 합니다.

5 **llm.asm** 은 11월 26일 글에서 849개였는데 이틀 만에 **2,447개** 가 됐습니다. 어셈블리 LLM 추론에 대한 관심이 계속 이어지고 있습니다.

목차

[1. 이번 주 흐름: 사람이 아니라 에이전트가 실행하는 CLI](#s1)

[2. safe-anything: 에이전트 설정까지 훑는 취약점 스캐너](#s2)

[3. fast-anything과 shrink-anything: 느린 5%만 다시 쓰는 접근](#s3)

[4. agent-sim: 맥 없이 리눅스에서 돌아가는 iOS 시뮬레이터](#s4)

[5. opengame과 llm.asm: 이틀 만에 세 배가 된 숫자](#s5)

[6. 이번 주 별 변화 한눈에 보기](#s6)

[정리 · 지금 해볼 것](#s-sum)

[자주 묻는 질문](#s-faq)

## 01 이번 주 흐름: 사람이 아니라 에이전트가 실행하는 CLI

이번 주 급상승 레포를 묶어 보면 공통 설계가 보입니다. **하나의 명령으로 끝나고, 설정 파일이 필요 없고, 결과를 종료 코드로 알려 주고, 같은 바이너리가 MCP 서버로도 동작합니다.** 사람이 쓰기 편한 구조이기도 하지만, 사실 이 네 가지는 에이전트가 도구를 쓰기 위한 최소 조건입니다. 에이전트는 설정 화면을 못 열고, 로그를 눈으로 훑지 못하고, 성공과 실패를 숫자로만 구분합니다.

| 레포 | 하는 일 | 언어 · 라이선스 | 에이전트 연결 방식 |
|----|----|----|----|
| safe-anything | 취약점·비밀키·설정 스캔 | Rust · MIT | MCP 서버 (scan, list_rules) |
| fast-anything | 느린 구간만 골라 재작성 | Rust · MIT | CLI, npm 전역 설치 |
| shrink-anything | 테스트 통과 유지하며 코드 축소 | Rust · MIT | CLI, npm 전역 설치 |
| agent-sim | 리눅스에서 iOS 시뮬레이터 구동 | Rust · Apache-2.0 | MCP 서버 (도구 15종) |
| opengame | 에이전트가 게임을 만드는 런타임 | TypeScript · Apache-2.0 | 로컬 에이전트 22종 내장 |

💡 왜 중요할까

지금까지 코딩 에이전트에게 부족했던 것은 모델의 능력보다 **검증 수단** 이었습니다. 에이전트가 코드를 고쳐도 그 결과가 안전한지, 빨라졌는지, 실제 기기에서 동작하는지 확인할 방법이 없으면 사람이 매번 손으로 봐야 합니다. 이번 주에 올라온 레포들은 전부 그 확인 단계를 자동화하는 쪽에 있습니다. 모델을 바꾸는 흐름이 아니라, 모델 주변의 도구를 채우는 흐름입니다.

## 02 safe-anything: 에이전트 설정까지 훑는 취약점 스캐너

safe-anything은 명령 한 번으로 코드의 취약점, 유출된 비밀키, 위험한 설정, 취약한 의존성을 찾는 Rust 스캐너입니다. 소개 문구는 "Find the holes before someone else does."입니다. 규칙은 **72개** 이고 각 규칙마다 CWE 번호와 OWASP 분류, 참고 링크가 붙습니다.

### 무엇을 검사하는가

코드는 JS/TS, 파이썬, Go, 자바, 코틀린, PHP, 루비, C#, SQL을 봅니다. 비밀키는 AWS, GitHub, Slack, Stripe, OpenAI, Anthropic, 구글 키와 `.env` 실수를 찾습니다. 설정은 도커, GitHub Actions, 쿠버네티스, 테라폼, nginx를 봅니다. 의존성은 락파일을 읽어 OSV.dev에 패키지 이름과 버전을 조회합니다.

이 레포에서 눈에 띄는 부분은 마지막 항목입니다. **에이전트 설정 자체를 검사 대상으로 넣었습니다.** MCP 서버 설정, Claude Code, Codex, Cursor, Gemini, OpenCode의 설정과 훅, 스킬이 포함됩니다. README는 그 이유를 "에이전트가 커밋하기 전에, 그리고 남의 스킬이나 MCP 서버를 설치하기 전에" 검사할 수 있도록 MCP 서버로도 제공한다고 적고 있습니다.

▶ safe-anything 설치와 실행

```
# 설치 (둘 중 하나)
cargo install safe-anything
npx safe-anything .

# 실행 - 설정 파일도, 계정도, 업로드도 없습니다
safe-anything .

# 높은 등급 이상이 나오면 종료 코드 1 (CI에서 바로 쓸 수 있습니다)
safe-anything . --severity medium --fail-on high

# 네트워크를 쓰지 않고 검사 (의존성 조회를 건너뜁니다)
safe-anything . --offline

# 에이전트에 MCP 서버로 붙이기
claude mcp add safe-anything -- safe-anything mcp
```

### 실제로 얼마나 잡는가

README에는 오픈소스 레포를 대상으로 돌린 결과가 적혀 있습니다. 애플 M4에서 `--offline` 기준 0.03초에서 0.13초가 걸렸고, 모든 결과를 손으로 확인했다고 밝히고 있습니다. 아래는 그 가운데 일부입니다.

| 대상 레포 | 검사 파일 | 발견 | 비고 |
|----|----|----|----|
| OWASP Juice Shop | 1,195개 | 67건 | 오탐 2~3건 (의도적으로 취약한 교육용 앱) |
| DVWA | 233개 | 63건 | 오탐 약 4건 (교육용 취약 앱) |
| expressjs/express | 216개 | 0건 | — |
| pallets/flask | 231개 | 2건 | — |
| modelcontextprotocol/servers | 439개 | 1건 | — |
| anthropics/skills | 392개 | 6건 | — |
| safe-anything 자신 | 53개 | 0건 | — |

📌 도구의 범위를 먼저 확인해야 합니다

README는 한계를 직접 적어 두었습니다. "알려진 패턴을 찾을 뿐, 프로그램 안에서 데이터가 어떻게 흐르는지는 따라가지 않는다"는 설명입니다. 즉 검사 결과가 깨끗하다는 말은 **이 72가지 문제가 발견되지 않았다는 뜻이고, 코드가 안전하다는 뜻은 아닙니다.** 가장 오탐이 많은 규칙으로는 `code.xss-inner-html`을 지목하고 있습니다.

[출처 · safe-anything ↗](https://github.com/erkamyaman/safe-anything) [출처 · OSV.dev ↗](https://osv.dev/)

## 03 fast-anything과 shrink-anything: 느린 5%만 다시 쓰는 접근

fast-anything은 이번 주 신규 레포 가운데 별이 가장 많이 붙었습니다. 레포 설명은 "전부 Rust로 다시 쓰지 말고, 느린 5%만 다시 쓰라"는 문장입니다. 프로그램 전체를 옮기는 대신 병목이 되는 함수만 Rust로 바꿔 끼우는 방식입니다.

README의 파이썬 중복 제거 예시 (기존)

4.91초

같은 작업을 바꿔 끼운 뒤

42밀리초

README는 이 차이를 **116배** 로 적고 있습니다. 어떤 작업이든 이만큼 빨라진다는 뜻은 아니고, 반복이 많고 계산이 단순한 구간에서 나오는 숫자로 보는 편이 맞습니다. 같은 저자(EL4CTEO)의 shrink-anything은 방향이 반대입니다. 기능을 유지하면서 코드 자체를 줄이고, 그 기준을 **테스트가 계속 통과하는지** 로 둡니다. README는 데모 앱에서 "읽어야 할 토큰이 46% 줄었다"고 적고 있습니다. 사람이 읽는 양이 아니라 에이전트가 읽어야 하는 양을 기준으로 삼은 표현입니다.

▶ 두 도구의 설치

```
# 느린 구간만 다시 쓰기
npm i -g @el4cteo/fast-anything

# 테스트를 통과시킨 채로 코드 줄이기
npm i -g @el4cteo/shrink-anything
```

💡 왜 중요할까

에이전트가 코드를 고칠 때 가장 큰 비용은 **코드를 읽는 양** 입니다. 파일이 길고 중복이 많으면 같은 작업에 더 많은 토큰이 들고, 그만큼 실수도 늘어납니다. shrink-anything이 성과를 토큰 수로 표시한 것은 이 도구의 사용자가 사람이 아니라 에이전트라는 뜻입니다. 코드 품질 도구의 지표가 바뀌고 있는 셈입니다.

[출처 · fast-anything ↗](https://github.com/EL4CTEO/fast-anything) [출처 · shrink-anything ↗](https://github.com/EL4CTEO/shrink-anything)

## 04 agent-sim: 맥 없이 리눅스에서 돌아가는 iOS 시뮬레이터

agent-sim은 소개 문구가 "iOS simulators for AI agents, on Linux"입니다. 애플의 iOS 시뮬레이터 런타임을 **x86-64 리눅스** 에서 돌리고, 에이전트가 iOS 앱을 시험할 수 있게 만듭니다. README는 "맥도 GPU도 필요 없다"고 적고 있습니다.

### 어떻게 가능한가

바탕은 x86Sim이라는 프로젝트입니다. Darling이 맥OS 커널 인터페이스를 제공하고, dynarmic이 ARM 코드를 번역하고, Mesa의 CPU Vulkan 드라이버가 metal2vulkan을 통해 Metal을 그립니다. agent-sim은 그 위에 미리 번역해 둔 런타임, 2배 해상도 렌더링, 접근성 트리를 읽는 훅, CLI와 MCP 서버, `.ipa` 변환, 기기 풀, 브라우저 스트리밍을 올렸습니다.

에이전트에게 중요한 부분은 `snapshot`입니다. 화면을 이미지로 넘기는 대신 앞에 있는 앱의 접근성 트리와 웹 페이지, 상태 바와 알림까지 **텍스트로 읽어 줍니다.** 그래서 에이전트가 이미지를 해석하지 않고도 요소를 찾아 탭하거나 입력할 수 있습니다.

| 항목 | README에 적힌 값 |
|----|----|
| 필요 환경 | 우분투 24.04, CPU 8개 이상, 메모리 16GB, 여유 디스크 60GB |
| 최초 설치 | 약 30분 (애플 iOS 런타임 8GB 내려받기 포함) |
| 기기 부팅 | 12~30초 (CPU에 따라) |
| 스크롤 성능 | Zen 5 가상 머신에서 약 55fps, 터치 지연 약 14밀리초 |
| 기기 풀 | 세 대를 함께 띄우면 8.7GB가 아니라 6.8GB 사용 (KSM) |
| 제약 | 암호화되지 않은 빌드만 실행. 앱스토어 내려받기(FairPlay)는 불가 |
| 상태 | "early" - 끝까지 동작하지만 거친 부분이 있다고 명시 |

▶ agent-sim 설치와 에이전트 연결

```
# 설치 (x86-64 리눅스)
curl -fsSL https://raw.githubusercontent.com/Developing-Gamer/agent-sim/main/install.sh | bash

agent-sim setup     # 최초 1회, 약 30분
agent-sim up        # 기기 부팅, 12~30초

# 앱 설치하고 화면을 텍스트로 읽기
agent-sim install MyApp.ipa
agent-sim launch com.example.myapp
agent-sim snapshot

# 요소를 찾아 조작하기
agent-sim tap @e4
agent-sim type "hello@example.com"
agent-sim wait "Welcome" --timeout 20

# 에이전트에 MCP 서버로 붙이기
claude mcp add agent-sim -- agent-sim mcp
```

📌 도입 전 확인할 점

설치 스크립트를 내려받아 바로 실행하는 방식이므로, 사내 장비나 공용 서버에 올릴 때는 스크립트 내용을 먼저 확인하는 편이 안전합니다. 라이선스는 Apache-2.0이지만 `patches/x86sim` 안의 패치는 x86Sim을 따라 GPL-3.0-or-later입니다. 애플 런타임은 레포에 들어 있지 않고 애플에서 직접 내려받습니다.

[출처 · agent-sim ↗](https://github.com/Developing-Gamer/agent-sim) [출처 · x86Sim ↗](https://github.com/x86sim/x86sim)

## 05 opengame과 llm.asm: 이틀 만에 세 배가 된 숫자

opengame은 별 2,592개로 이번 주 신규 레포 중 두 번째입니다. 레포 설명은 "The Super Game Agent - the Unity & Unreal for AI agents"입니다. 에이전트가 게임을 만들고 플레이하는 런타임을 지향하고, README는 바로 플레이할 수 있는 템플릿 25종과 로컬 에이전트 22종을 내장했다고 적고 있습니다. 실행에는 Node 22.18 이상이 필요합니다.

llm.asm은 저희가 [11월 26일 AI 트렌드 글](https://dongseodong.tistory.com/69)에서 다룬 레포입니다. 그때 별이 849개였는데 지금은 **2,447개** 입니다. x86-64 어셈블리만으로 Qwen3-0.6B 추론을 구현한 프로젝트이고, 바이너리 크기는 14,712바이트입니다. README는 40스레드에서 최고 126.8 tok/s를 기록했고, Q8_0 기준 llama.cpp의 CPU 추론보다 18~36% 빠르다고 적고 있습니다.

11월 26일 글 작성 당시

별 849개

11월 28일 저녁

별 2,447개

이틀 사이에 세 배 가까이 늘었습니다. 한 주짜리 신규 레포의 별 수는 이렇게 빠르게 변하기 때문에, 이 글의 숫자도 보시는 시점에는 달라져 있을 가능성이 큽니다. 숫자보다 흐름을 보시는 편이 좋습니다.

## 06 이번 주 별 변화 한눈에 보기

fast-anything (Rust) **4,574**

opengame (TypeScript) **2,592**

llm.asm (Assembly) **2,447**

KuroCat (TypeScript) **1,847**

waifu2x-image-upscaler-windows (C++) **1,083**

f-ck_data_brokers (Python) **997**

safe-anything (Rust) **843**

PiBot (TypeScript) **689**

agent-sim (Rust) **631**

shrink-anything (Rust) **410**

ARTEX-CC (Go) **292**

2026년 11월 28일 저녁 GitHub API 기준. 모두 11월 21일 이후에 만들어진 신규 레포입니다.

목록을 보면 Rust가 네 개, TypeScript가 세 개입니다. 사람이 직접 쓰는 앱보다 **에이전트가 호출하는 바이너리** 가 많은 주였습니다.

📌 숫자를 볼 때 함께 보면 좋은 지표

한 가지 사실을 덧붙입니다. waifu2x-image-upscaler-windows는 레포가 만들어진 뒤 2분 만에 마지막 푸시가 있었고 이후 커밋이 없습니다. 별 1,083개에 포크는 0개입니다. 같은 목록의 다른 레포들은 포크가 별의 7~15% 수준입니다. 이 레포가 그 패턴과 다르다는 사실만 적어 둡니다. 원인은 저희가 확인하지 못했습니다.

## 정리

**이번 주의 흐름:** 모델이 아니라 모델이 쓸 도구가 쏟아진 주였습니다. 전부 단일 명령 CLI이면서 MCP 서버로 붙습니다.

**safe-anything:** 72개 규칙으로 코드·비밀키·설정·의존성을 검사하고, 에이전트 설정 자체도 검사 대상에 넣었습니다.

**fast-anything · shrink-anything:** 느린 구간만 Rust로 바꾸거나, 테스트를 통과시킨 채로 코드를 줄입니다. 성과를 토큰 수로 표시한 점이 특징입니다.

**agent-sim:** 맥 없이 리눅스에서 iOS 시뮬레이터를 돌리고, 화면을 텍스트로 읽어 에이전트가 조작합니다. 상태는 아직 초기입니다.

✦ 지금 해볼 것

☐ 팀 레포에서 `npx safe-anything .` 를 한 번 돌려 보고, 유출된 키가 잡히는지만 먼저 확인하기

☐ CI에 `--fail-on high` 로 넣어 보고, 오탐이 많으면 `--severity` 로 등급을 조절하기

☐ MCP 서버나 남이 만든 스킬을 설치하기 전에 해당 디렉터리를 먼저 검사하기

☐ 성능 병목이 분명한 함수가 있다면 fast-anything으로 그 구간만 바꿔 보고 측정값을 비교하기

## 자주 묻는 질문

### Q. safe-anything 하나로 보안 점검을 끝낼 수 있나요?

그렇지 않습니다. README가 직접 밝히듯 알려진 패턴을 찾는 도구이고, 프로그램 안에서 데이터가 어떻게 흐르는지는 추적하지 않습니다. 검사 결과가 깨끗하다는 말은 72가지 규칙에 걸리는 것이 없다는 뜻입니다. 기존 코드 리뷰나 의존성 관리, 침투 테스트를 대체하는 도구로 보기는 어렵고, 커밋 전에 거르는 1차 관문으로 쓰는 편이 맞습니다.

### Q. fast-anything의 116배 같은 숫자를 그대로 기대해도 되나요?

어렵습니다. README의 116배는 파이썬 중복 제거라는 특정 작업에서 나온 값입니다. 반복이 많고 계산이 단순한 구간일수록 효과가 크고, 입출력이나 네트워크를 기다리는 구간에서는 거의 차이가 없습니다. 먼저 프로파일러로 병목을 찾고, 그 구간만 바꾼 뒤 직접 측정해 보시는 순서를 권합니다.

### Q. agent-sim을 쓰면 맥 없이 iOS 앱을 개발할 수 있나요?

시험까지는 가능하지만 개발 전체를 대체하지는 못합니다. 암호화되지 않은 빌드만 실행되므로 앱스토어에서 내려받은 앱은 열리지 않고, 애플 런타임도 사용자가 직접 애플에서 내려받아야 합니다. README 스스로 상태를 "early"로 적고 있습니다. 에이전트가 자동으로 화면을 훑는 회귀 시험 용도에 먼저 써 보시는 편이 좋습니다.

------------------------------------------------------------------------

**참고 링크**

[출처 · safe-anything ↗](https://github.com/erkamyaman/safe-anything) [출처 · fast-anything ↗](https://github.com/EL4CTEO/fast-anything) [출처 · shrink-anything ↗](https://github.com/EL4CTEO/shrink-anything) [출처 · agent-sim ↗](https://github.com/Developing-Gamer/agent-sim) [출처 · opengame ↗](https://github.com/nexu-io/opengame) [출처 · llm.asm ↗](https://github.com/alesha-pro/llm.asm)

---

`#AI트렌드` `#깃허브트렌드` `#safe-anything` `#fast-anything` `#agent-sim` `#MCP` `#러스트` `#코딩에이전트` `#iOS시뮬레이터` `#오픈소스`
