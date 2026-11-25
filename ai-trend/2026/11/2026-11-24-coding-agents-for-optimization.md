---
title: "오늘의 AI 트렌드 (2026.11.24) - 코딩 에이전트에게 '최적화'를 맡기는 레포들"
date: 2026-11-24
category: "AI 트렌드"
tistory: https://dongseodong.tistory.com/60
tags: ["AI트렌드", "claudecode", "GitHub", "LLM추론", "rust", "깃허브트렌드", "로컬llm", "모바일테스트", "성능최적화", "코딩에이전트"]
cover: assets/2026-11-24-coding-agents-for-optimization.jpg
---
# 오늘의 AI 트렌드 (2026.11.24) - 코딩 에이전트에게 '최적화'를 맡기는 레포들

> 📈 **AI 트렌드** · 2026-11-24 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/60)

![대표 이미지](assets/2026-11-24-coding-agents-for-optimization.jpg)

11월 10일 이후 새로 만들어진 AI 레포 중 별(⭐)이 빠르게 모인 곳들을 모아 봤어요. 이번 주 상위권을 보면 흐름이 하나로 모여요. 코드를 처음부터 짜는 에이전트를 넘어, **측정하고 검증하고 테스트하는 일** 을 에이전트에게 맡기는 도구들이 뜨고 있어요. 오늘은 그중 세 개를 골라 **어떤 문제를 푸는지, 어떻게 동작하는지, 직접 써보려면 뭘 치면 되는지** 까지 정리해 볼게요.

TL;DR · 한눈에 보기

1 **fast-anything** : 앱에서 느린 함수만 골라 Rust로 포팅시키고, 실제 호출을 다시 돌려 결과가 같다는 걸 증명한 뒤에 바꿔 끼워요.

2 **inference-optimisation-skill** : 로컬 LLM 서빙 속도를 "이론 한계 계산 → 하나씩 바꾸기 → 대조군 비교" 절차로 올리는 에이전트 스킬이에요.

3 **mobile-agent-testers** : GitHub Actions 무료 러너에 폰 20대를 띄우고 AI 테스터를 붙여, 몇 달러로 수십 개 버그를 찾아요.

| 레포                                         | ⭐ (11/24 기준) | 한 줄 요약                      |
|----------------------------------------------|-----------------|---------------------------------|
| deepseek-ai/chat-demo                        | 5,374           | DeepSeek 공식 채팅 데모         |
| EL4CTEO/fast-anything                        | 3,402           | 느린 함수만 골라 Rust로 포팅    |
| Immortal-Protocols/lastbook                  | 3,027           | 오프라인 지식 AI·지도·영상 묶음 |
| sybil-solutions/inference-optimisation-skill | 2,381           | 로컬 LLM 서빙 속도 튜닝 스킬    |
| iamajmeena/neonclipping                      | 2,374           | 링크로 9:16 숏폼 자동 생성      |
| pierridotite/mobile-agent-testers            | 1,630           | AI 테스터가 폰 20대로 앱 QA     |
| huggingface/pybot                            | 1,158           | 에이전트들이 짠 규칙 기반 챗봇  |

목차

[1. fast-anything: 느린 5%만 Rust로, 증명하고 바꾸기](#s1)

[2. inference-optimisation-skill: 로컬 LLM 속도를 과학적으로](#s2)

[3. mobile-agent-testers: AI 테스터 20명이 폰 20대로](#s3)

[4. 세 레포가 보여주는 흐름](#s4)

[정리](#s-sum)

## 01 fast-anything: 느린 5%만 Rust로, 증명하고 바꾸기

### 어떤 문제를 푸나

앱이 느리다고 전체를 Rust로 다시 짜면 몇 달이 걸려요. 그런데 실제 실행 시간은 대부분 **몇 개 함수에 몰려 있는** 경우가 많아요. fast-anything은 그 함수만 찾아서 코딩 에이전트(Claude Code, Codex 등)에게 Rust로 포팅을 맡기고, 원본과 결과가 똑같다는 게 확인된 뒤에만 바꿔 끼워요.

### 동작 원리

STEP 1

**scan**  
프로파일링 후 "걸리는 시간 × 포팅 난이도"로 함수 순위 매기기

STEP 2

**port**  
실제 호출을 최대 500개 녹화, 함수 하나짜리 Rust 크레이트와 TASK.md 생성

STEP 3

**verify**  
녹화한 호출과 자동 생성한 엣지 케이스를 전부 다시 돌려 비교

STEP 4

**enable**  
통과하면 교체, 언제든 disable로 되돌리기

핵심은 verify 단계예요. 녹화된 호출 말고도 NaN, 무한대, -0.0, 비ASCII 문자, 빈 입력 같은 엣지 케이스를 자동으로 만들어 원본과 비교해요. 실수(float)는 1e-9 오차 안에서 같아야 통과해요. README에는 겉보기엔 맞는 포팅이었는데 문자 대신 바이트를 비교하고 있어서 **500개 호출 중 148개** 에서 걸린 사례가 나와요. 테스트 몇 개로는 못 잡았을 버그예요.

Rust 쪽 호출 비용 때문에 오히려 느려지는 함수라면 적용하지 않아요. 빨라지는 경우에만 바꾸는 거죠.

### 얼마나 빨라지나

Python 퍼지 중복 제거 (원본) **4.91초**

Python → Rust 포팅 후 **42ms**

TypeScript 버전 (원본) **3.11초**

TypeScript → Rust 포팅 후 **155ms**

README 측정값 기준. Python은 약 116배, TypeScript는 약 20배 빨라졌어요. Python, Node, Ruby, Java, Go, PHP 등 8개 언어 벤치마크가 있어요. MIT 라이선스.

### 직접 써보기

설치는 npm이나 cargo 중 편한 쪽으로 하면 돼요. 그다음 평소 앱을 실행하던 명령 앞에 붙여서 돌리면 에이전트가 스캔부터 포팅, 검증까지 진행해요.

▶ 설치 (둘 중 하나)

```
npm i -g @el4cteo/fast-anything
# 또는
cargo install fast-anything
```

▶ Claude Code에게 맡겨서 Python 앱 최적화하기

```
fast-anything go --agent claude -- python app.py
```

📌 써볼 때 팁

포팅된 함수는 원본 코드 옆에 붙는 형태라, 문제가 생기면 disable로 바로 원래 구현으로 돌아갈 수 있어요. 처음엔 배치 작업이나 데이터 정제처럼 **입출력이 분명한 순수 함수** 에 먼저 써 보는 걸 권해요.

💡 왜 중요할까

"AI가 짠 코드를 믿어도 되나?"라는 질문에 **"실제 호출로 증명하라"** 는 답을 도구로 만든 사례예요. 코드 리뷰로 신뢰를 쌓는 대신 녹화된 실제 입력으로 동치성을 검사하니, 에이전트에게 맡길 수 있는 작업의 범위가 넓어져요.

[출처 · GitHub · fast-anything ↗](https://github.com/EL4CTEO/fast-anything)

------------------------------------------------------------------------

## 02 inference-optimisation-skill: 로컬 LLM 속도를 과학적으로

### 무엇인가

로컬에서 LLM 서버를 돌릴 때 속도를 단계적으로 끌어올리는 방법을 **에이전트 스킬(SKILL.md)** 로 정리한 레포예요. 플래그 목록이 아니라, 실제로 속도를 올렸던 작업 방식을 담았어요. 다루는 범위는 디코딩, 투기적 디코딩(speculative decoding), 프리필, KV 캐시 크기, 첫 토큰까지 걸리는 시간(TTFT)이에요.

### 작업 원리: 감 대신 측정

STEP 1

**한계 계산**  
토큰당 읽는 바이트 ÷ 메모리 대역폭으로 이론상 최고 속도 구하기

STEP 2

**하나씩 변경**  
한 번에 설정 하나만 바꾸기

STEP 3

**대조군 비교**  
번갈아 돌린 이웃 대조군보다 빨라야 채택

STEP 4

**회귀 확인**  
다른 지표가 3% 넘게 나빠지면 기각, 실패도 기록

처음에 이론 한계를 계산하게 하는 게 핵심이에요. 목표가 물리적으로 불가능하면 에이전트가 시간을 쓰기 전에 알려줄 수 있거든요. 레포에는 이 절차를 돕는 스크립트로 한계를 계산하는 **ceiling.py** , 실험을 줄 세우는 **queue.sh** , 측정하는 **bench.py** 가 들어 있어요. 긴 컨텍스트에서 정보를 제대로 찾는지도 확인한 뒤에만 변경을 통과시켜요.

### README에 나온 결과

인텔 Arc B390 디코딩 (튜닝 전) **43.6 tok/s**

인텔 Arc B390 디코딩 (튜닝 후) **53 tok/s**

RTX 3090 · 27B 모델 (기준) **96.2 tok/s**

RTX 3090 · 27B 모델 (튜닝 후) **141.1 tok/s**

README 측정값 기준. RTX 3090에서는 약 47%, 노트북 내장 GPU에서도 약 22% 올랐어요.

### 설치해서 쓰기

Claude Code 스킬 폴더에 복사하면 끝이에요. 그다음 에이전트에게 "내 llama.cpp 서버 디코딩 속도 올려줘"처럼 요청하면 스킬의 절차를 따라 진행해요.

▶ Claude Code 스킬로 설치

```
git clone https://github.com/sybil-solutions/inference-optimisation-skill
mkdir -p ~/.claude/skills
cp -r inference-optimisation-skill/skills/inference-optimisation ~/.claude/skills/
```

| 상황                          | 먼저 볼 지표                          |
|-------------------------------|---------------------------------------|
| 채팅이 답답하게 느껴짐        | 디코딩 tok/s, 투기적 디코딩 적용 여부 |
| 긴 문서를 넣으면 첫 답이 늦음 | 프리필 속도, TTFT                     |
| 컨텍스트를 늘리면 메모리 부족 | KV 캐시 크기와 양자화 설정            |

💡 왜 중요할까

로컬 LLM을 쓰는 사람이 늘면서, 지금까지 "감으로 튜닝하던" 영역이 **측정 기반 절차** 로 바뀌고 있어요. 그 절차를 사람이 아니라 에이전트가 따라 하게 만든 게 이 레포의 포인트예요. 같은 방식은 DB 튜닝이나 빌드 속도 개선에도 그대로 옮길 수 있어요.

[출처 · GitHub · inference-optimisation-skill ↗](https://github.com/sybil-solutions/inference-optimisation-skill)

------------------------------------------------------------------------

## 03 mobile-agent-testers: AI 테스터 20명이 폰 20대로

### 무엇인가

GitHub Actions 무료 러너 위에 iOS 시뮬레이터와 안드로이드 에뮬레이터를 띄우고, 각각에 Claude Code 에이전트를 테스터로 붙이는 템플릿이에요. **테스트 스크립트를 따로 쓸 필요가 없어요.** Flutter, React Native, Expo, 네이티브 Kotlin·Swift 앱을 지원해요.

### 어떻게 테스트하나

에이전트마다 "페르소나"가 있어요. 가장 큰 글자 크기를 쓰는 스웨덴어 사용자의 iPhone SE, 200% 확대한 Pixel 7, 아랍어처럼 오른쪽에서 왼쪽으로 쓰는 사용자 같은 식이에요. 각자 새 사용자처럼 앱을 써 보고 **스크린샷이 붙은 버그 리포트** 를 남겨요. 특정 기능을 끝까지 따라가게 하거나, 받은 버그 리포트가 모든 기기에서 재현되는지 확인시킬 수도 있어요.

### 비용 대비 결과

| 대상 앱                     | 찾은 문제 | 모델 비용 |
|-----------------------------|-----------|-----------|
| LocalSend                   | 버그 46개 | \$4.62    |
| AnkiDroid                   | 이슈 43개 | \$4.69    |
| 데모 앱 (버그 11개 심어 둠) | 9개 발견  | \$0.87    |

공개 레포라면 러너는 무료이고, 모델 비용만 기기당 대략 0.15~0.55달러 들었다고 해요. AnkiDroid에서는 새 카드의 뒷면 입력칸이 키보드에 가려지는 버그를 찾았는데, 사람이 큰 글자·작은 화면 조합으로 매번 확인하기는 어려운 종류예요.

### 내 앱에 붙여 보기

▶ 템플릿으로 내 테스터 레포 만들고 실행하기

```
gh repo create my-testers --public --template pierridotite/mobile-agent-testers --clone
cd my-testers
./setup.sh                          # 초기 설정 (안내에 따라 진행)
gh workflow run agent-testers.yml   # 기기들에서 AI 테스터 실행
bash scripts/collect.sh <run id>    # 버그 리포트와 스크린샷 모으기
```

⚠ 비용과 키 관리

비공개 레포에서 돌리면 GitHub Actions macOS 러너 시간이 과금될 수 있어요. 처음엔 기기 수를 줄여서 비용을 확인한 뒤 늘리는 게 안전해요. API 키는 레포 Secrets에만 넣고 코드에 적지 마세요.

💡 왜 중요할까

다국어, 큰 글자, 작은 화면처럼 **사람이 매번 챙기기 어려운 조합** 을 병렬로, 커피 한 잔 값에 돌릴 수 있어요. 접근성 QA가 "출시 전에 한 번"이 아니라 PR마다 도는 일이 될 수 있다는 점에서 실무 임팩트가 커요.

[출처 · GitHub · mobile-agent-testers ↗](https://github.com/pierridotite/mobile-agent-testers)

## 04 세 레포가 보여주는 흐름

세 레포 모두 에이전트에게 일을 맡기되, **결과를 기계적으로 확인하는 장치** 를 함께 만들었어요. fast-anything은 녹화된 호출로, inference 스킬은 대조군 측정으로, mobile-agent-testers는 스크린샷이 붙은 재현 리포트로 검증해요.

지난 흐름

"코드를 짜 줘"

이번 주 흐름

"측정하고 증명해 줘"

> 에이전트가 강해질수록, 사람이 할 일은 "검증 기준을 정하는 것"으로 옮겨가고 있어요.

그 밖에 DeepSeek 공식 채팅 데모(chat-demo), 오프라인 지식 묶음 lastbook, 링크 하나로 숏폼을 만드는 neonclipping도 별이 빠르게 모였어요. 관심 있다면 표의 레포 이름으로 검색해 보세요.

## 정리

**fast-anything:** 느린 함수만 Rust로 포팅하고, 실제 호출 500개와 엣지 케이스로 동치성을 증명한 뒤 교체해요.

**inference-optimisation-skill:** 이론 한계 계산과 대조군 비교로 로컬 LLM 속도를 올리는 절차를 에이전트에게 맡겨요.

**mobile-agent-testers:** 폰 20대에 AI 테스터를 붙여 몇 달러로 수십 개 버그를 찾아요.

✦ 지금 해볼 것

☐ 느린 Python 스크립트 하나 골라서 fast-anything go로 돌려 보기

☐ 로컬 LLM을 쓰고 있다면 inference-optimisation 스킬 설치하고 현재 tok/s부터 측정하기

☐ 사이드 프로젝트 앱에 mobile-agent-testers 템플릿 붙여서 기기 2~3대로 먼저 돌려 보기

---

`#AI트렌드` `#claudecode` `#GitHub` `#LLM추론` `#rust` `#깃허브트렌드` `#로컬llm` `#모바일테스트` `#성능최적화` `#코딩에이전트`
