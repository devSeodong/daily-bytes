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

## 한눈에 보기

11월 10일 이후 새로 만들어진 AI 관련 GitHub 레포 중 스타가 많이 모인 곳들이에요. 스타 수는 11월 24일 기준입니다.

- [deepseek-ai/chat-demo](https://github.com/deepseek-ai/chat-demo) ⭐ 5,374: DeepSeek 공식 채팅 데모
- [EL4CTEO/fast-anything](https://github.com/EL4CTEO/fast-anything) ⭐ 3,402: 느린 함수만 골라 Rust로 포팅
- [Immortal-Protocols/lastbook](https://github.com/Immortal-Protocols/lastbook) ⭐ 3,027: 오프라인 지식 AI, 지도, 영상 묶음
- [sybil-solutions/inference-optimisation-skill](https://github.com/sybil-solutions/inference-optimisation-skill) ⭐ 2,381: 로컬 LLM 서빙 속도 튜닝 스킬
- [iamajmeena/neonclipping](https://github.com/iamajmeena/neonclipping) ⭐ 2,374: 링크로 9:16 숏폼 자동 생성
- [pierridotite/mobile-agent-testers](https://github.com/pierridotite/mobile-agent-testers) ⭐ 1,630: AI 테스터 20명이 폰 20대로 앱 QA
- [huggingface/pybot](https://github.com/huggingface/pybot) ⭐ 1,158: 에이전트들이 짠 규칙 기반 챗봇

이번 주 흐름은 분명해요. 코드를 '처음부터 짜는' 에이전트를 넘어, **측정하고 검증하는 일** 을 에이전트에게 맡기는 도구들이 뜨고 있습니다. 그중 세 개를 자세히 볼게요.

## 1. fast-anything: "Rust로 다 다시 짜지 말고, 느린 5%만"

### 어떤 문제를 푸나

앱이 느리다고 전체를 Rust로 다시 짜면 몇 달이 걸립니다. 그런데 실제 실행 시간의 대부분은 몇 개 함수에 몰려 있는 경우가 많아요. fast-anything은 그 함수만 찾아서 코딩 에이전트(Claude Code, Codex 등)에게 Rust로 포팅시키고, 원본과 결과가 똑같은지 증명한 뒤에 바꿔 끼웁니다.

### 동작 순서

1.  `scan`: 앱을 프로파일링해서 "걸리는 시간 × 포팅 난이도"로 함수 순위를 매깁니다.
2.  `port`: 해당 함수의 실제 호출을 최대 500개 녹화하고, 함수 하나짜리 Rust 크레이트와 에이전트용 작업 지시서(TASK.md)를 만듭니다.
3.  `verify`: 녹화한 호출을 전부 다시 돌려서 결과를 비교합니다.
4.  `enable` / `disable`: 검증을 통과하면 바꿔 끼우고, 언제든 되돌릴 수 있습니다.

### 핵심은 검증

README에 나온 예시가 좋아요. 겉보기엔 맞는 포팅이었는데 문자 대신 바이트를 비교하고 있었고, 녹화된 500개 호출 중 148개에서 걸렸다고 합니다. 녹화된 호출 말고도 NaN, 무한대, -0.0, 비ASCII 문자, 빈 입력 같은 엣지 케이스를 자동으로 만들어 원본 결과와 비교해요. Rust 호출 비용 때문에 오히려 느려지는 경우에도 적용하지 않습니다.

README의 측정 결과로는 Python 퍼지 중복 제거가 4.91초에서 42ms(116배), TypeScript 버전이 3.11초에서 155ms(20배)로 줄었습니다. Python, Node, Ruby, Java, Go, PHP 등 여러 언어를 지원하고 MIT 라이선스예요.

왜 주목할까: AI가 짠 코드를 믿을 수 있느냐는 질문에 "실제 호출로 증명하라"는 답을 도구로 만든 사례입니다.

## 2. inference-optimisation-skill: 로컬 LLM 속도를 '과학적으로' 올리기

### 무엇인가

로컬에서 LLM 서버를 돌릴 때 속도를 단계적으로 끌어올리는 방법을 에이전트 스킬(SKILL.md)로 정리한 레포입니다. 단순한 플래그 목록이 아니라 실제로 속도를 올렸던 작업 방식을 담았다고 해요. 디코딩, 투기적 디코딩(speculative decoding), 프리필, KV 캐시 크기, 첫 토큰까지 걸리는 시간(TTFT)을 다룹니다.

### 작업 방식

1.  먼저 이론상 한계를 계산합니다. 토큰당 읽는 바이트를 메모리 대역폭으로 나누는 식이에요.
2.  한 번에 하나만 바꿉니다.
3.  번갈아 돌린 대조군과 비교해서 측정합니다.
4.  실패한 시도까지 모두 기록합니다.
5.  긴 컨텍스트에서도 정보를 제대로 찾는지 확인한 뒤에만 통과시킵니다.

처음에 이론적 한계를 계산하게 하는 게 핵심이에요. 목표가 물리적으로 불가능하면 에이전트가 일찍 알려줄 수 있거든요. README에 따르면 RTX 3090에서 한 MoE 모델이 1인 기준 초당 251.7 토큰(코드는 357.9)까지 나왔고, 인텔 Arc 노트북 내장 GPU에서는 256K 프리필 속도가 2.1배 빨라졌다고 합니다.

왜 주목할까: 로컬 LLM 붐 속에서 "감으로 튜닝하던" 영역을 측정 기반 절차로 바꾸고, 그 절차를 에이전트가 따라 하게 만들었다는 점이에요.

## 3. mobile-agent-testers: AI 테스터 20명이 폰 20대로

### 무엇인가

GitHub Actions 무료 러너 위에 iOS 시뮬레이터와 안드로이드 에뮬레이터를 띄우고, 각각에 Claude Code 에이전트를 테스터로 붙입니다. 테스트 스크립트를 따로 쓸 필요가 없어요.

### 어떻게 테스트하나

에이전트마다 '페르소나'가 있습니다. 예를 들면 가장 큰 글자 크기를 쓰는 스웨덴어 사용자의 iPhone SE, 200% 확대한 Pixel 7, 아랍어(오른쪽에서 왼쪽 쓰기)를 쓰는 사용자 같은 식이에요. 각자 새 사용자처럼 앱을 써보고 스크린샷이 붙은 버그 리포트를 남깁니다. 특정 기능을 끝까지 따라가 보게 하거나, 버그 리포트를 받아 모든 기기에서 재현되는지 확인하게 할 수도 있어요.

Flutter, React Native, Expo, 네이티브 Kotlin·Swift 등을 지원합니다. 공개 레포라면 러너는 무료이고, 모델 비용만 기기당 약 0.15~0.55달러 들었다고 해요. 실제로 AnkiDroid에서는 새 카드의 뒷면 입력칸이 키보드에 가려지는 버그를 찾았다고 합니다.

왜 주목할까: 다국어, 큰 글자, 작은 화면처럼 사람이 매번 챙기기 어려운 조합을 병렬로 저렴하게 돌릴 수 있다는 점이 실무에 바로 와닿아요.

---

`#AI트렌드` `#claudecode` `#GitHub` `#LLM추론` `#rust` `#깃허브트렌드` `#로컬llm` `#모바일테스트` `#성능최적화` `#코딩에이전트`
