---
title: "AI가 뒤집어놓은 수학계 ③ VP ≠ VNP, 47년 난제를 4시간 차이로 풀었다고 발표한 Claude와 OpenAI"
date: 2026-11-28
category: "AI 심층 분석"
tistory: https://dongseodong.tistory.com/83
tags: ["VPVNP", "발리언트추측", "계산복잡도", "PvsNP", "퍼머넌트", "Claude", "OpenAI", "Lean", "AI수학", "AI심층분석"]
cover: assets/2026-11-28-ai-math-03-vp-vnp.png
---
# AI가 뒤집어놓은 수학계 ③ VP ≠ VNP, 47년 난제를 4시간 차이로 풀었다고 발표한 Claude와 OpenAI

> 🔬 **AI 심층 분석** · 2026-11-28 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/83)

![대표 이미지](assets/2026-11-28-ai-math-03-vp-vnp.png)

2026년 11월 23일 밤(UTC), Anthropic이 깃허브에 70쪽짜리 논문 하나를 올렸습니다. 제목은 **"VP ≠ VNP over every field"** , 저자는 **"Claude (Anthropic)"** 였습니다. 그리고 약 4시간 뒤 OpenAI도 같은 문제의 증명을 자기 저장소에 올렸습니다. 1979년부터 열려 있던 계산복잡도의 핵심 난제, 흔히 "대수판 P vs NP"라고 불리는 문제를 두 AI 회사가 몇 시간 차이로 풀었다고 발표한 것입니다. 이 글에서는 VP와 VNP가 무엇인지, 두 회사가 정확히 무엇을 공개했는지, 그리고 P vs NP와는 무엇이 다른지를 정리합니다.

TL;DR · 한눈에 보기

1 **VP ≠ VNP** 는 1979년 레슬리 발리언트가 제시한 문제로, "행렬식처럼 쉽게 계산되는 다항식"과 "퍼머넌트처럼 어려워 보이는 다항식"이 정말 다른지를 묻습니다.

2 **2026년 11월 23일** Anthropic이 Claude가 만든 70쪽 논문과 Lean 증명(약 7만 3천 줄)을 공개했고, **약 4시간 뒤** OpenAI도 자체 증명을 공개했습니다.

3 Lean 검사는 통과했다고 보고되었지만 **사람의 한 줄 한 줄 검토와 동료 심사는 아직** 이며, 이 결과가 P ≠ NP를 증명하는 것은 아닙니다.

📚 AI가 뒤집어놓은 수학계 시리즈

1탄 · 리만 가설 [167년 난제에 AI가 두 번 도전한 이야기](https://dongseodong.tistory.com/81)

2탄 · 양자 알고리즘 [AI가 양자 회로를 설계하고 증명까지](https://dongseodong.tistory.com/82)

3탄 · VP ≠ VNP **Claude와 OpenAI, 몇 시간 차이의 증명 공개** 지금 읽는 글

4탄 · OpenAI 9편 하루에 올라온 수학 논문 아홉 편예정

5탄 · 구글 6편 Cogentic과 소인수분해 난제예정

목차

[1. VP와 VNP는 무엇인가](#s1)

[2. AI가 한 일: 4시간 차이로 공개된 두 증명](#s2)

[3. VP ≠ VNP와 P ≠ NP는 무엇이 다를까](#s3)

[4. 앞으로 벌어질 일](#s4)

## 01 VP와 VNP는 무엇인가

**한 줄 요약:** VP는 "효율적으로 계산할 수 있는 다항식"의 모임이고, VNP는 "효율적으로 정의할 수는 있지만 계산이 쉬운지는 모르는 다항식"의 모임입니다.

### 비유로 이해하기: 쌍둥이처럼 생긴 두 공식

고등학교에서 배우는 2×2 행렬의 **행렬식** 은 `ad − bc`입니다. 그런데 부호를 바꿔 `ad + bc`로 만든 것을 **퍼머넌트** 라고 합니다. 공식 모양은 거의 쌍둥이입니다. 부호 하나만 다릅니다.

그런데 행렬이 커지면 이 쌍둥이의 운명이 완전히 갈립니다. 행렬식은 가우스 소거법으로 n×n 행렬에서도 n³ 정도의 계산이면 끝납니다. 반면 퍼머넌트는 지금까지 알려진 가장 좋은 방법(1963년 Ryser 공식)도 2<sup>n</sup>에 가까운 계산이 필요합니다. **"부호 하나 차이인데 정말 이렇게 어려운가, 아니면 우리가 아직 영리한 방법을 못 찾은 것인가"** 가 바로 VP 대 VNP 문제의 핵심입니다.

| 구분 | 행렬식 (determinant) | 퍼머넌트 (permanent) |
|----|----|----|
| 2×2 공식 | ad − bc | ad + bc |
| 계산 방법 | 가우스 소거법, 약 n³ | Ryser 공식, 약 n·2<sup>n</sup> |
| 속한 모임 | VP (쉬움) | VNP 완전 (VNP에서 가장 어려운 대표) |
| 쓰이는 곳 | 선형대수 전반 | 조합론(완전 매칭 개수 세기), 양자 광학(보손 샘플링) |

직접 계산해 보면 차이가 체감됩니다. 아래 코드는 행렬 크기를 늘려 가며 행렬식과 퍼머넌트 계산 시간을 비교합니다.

▶ 행렬식과 퍼머넌트 계산 시간 비교해 보기

```
import itertools, time
import numpy as np

def permanent(M):
    """Ryser 공식: 약 n * 2^n 번의 계산이 필요합니다"""
    n = len(M)
    total = 0
    for k in range(1, n + 1):
        for cols in itertools.combinations(range(n), k):
            prod = 1
            for row in M:
                prod *= sum(row[c] for c in cols)
            total += (-1) ** k * prod
    return (-1) ** n * total

for n in [8, 12, 16, 20]:
    M = np.random.randint(0, 3, size=(n, n)).tolist()

    t = time.time(); np.linalg.det(np.array(M, dtype=float)); t_det = time.time() - t
    t = time.time(); permanent(M); t_per = time.time() - t

    print(f"n={n:2d}  행렬식 {t_det*1000:8.3f} ms   퍼머넌트 {t_per*1000:10.1f} ms")
# n이 4 늘 때마다 퍼머넌트 시간만 수십 배씩 커집니다
```

### 대수 회로라는 무대

VP와 VNP는 **대수 회로** 라는 계산 모델 위에서 정의됩니다. 덧셈(+)과 곱셈(×) 게이트만으로 다항식을 만들어 가는 회로입니다. 회로 크기가 n의 다항식 정도로 작게 유지되는 다항식 가족이 VP이고, 그런 다항식들을 지수적으로 많이 더한 형태로 쓸 수 있는 가족이 VNP입니다. 발리언트는 1979년에 퍼머넌트가 VNP에서 가장 어려운 문제(VNP 완전)임을 보였고, 그래서 **"VP ≠ VNP"는 "퍼머넌트는 작은 대수 회로로 계산할 수 없다"와 같은 말** 이 되었습니다. 이 명제는 흔히 발리언트 추측이라고 불립니다.

💡 왜 오래 풀리지 않았을까

어떤 계산이 '불가능하다'를 보이려면, 앞으로 누가 생각해 낼지 모르는 모든 영리한 회로가 실패한다는 것을 증명해야 합니다. 이런 '하한' 증명은 계산복잡도에서 가장 어려운 종류의 문제로 꼽히며, 지금까지 알려진 퍼머넌트 회로 하한은 목표와 거리가 아주 멀었습니다.

## 02 AI가 한 일: 4시간 차이로 공개된 두 증명

**한 줄 요약:** Anthropic은 2026년 11월 23일 Claude가 만든 증명을, OpenAI는 약 4시간 뒤 11월 6일에 얻었다는 증명을 각각 깃허브에 공개했습니다.

### 타임라인

| 시각 (UTC) | 사건 |
|----|----|
| 11월 6일 | OpenAI가 나중에 공개한 기록상, VP ≠ VNP 결과를 얻은 날짜 |
| 11월 23일 20:04 | Anthropic이 `anthropics/formal-math` 저장소에 `vp-vnp` 폴더 커밋 (21:43 병합) |
| 11월 24일 01:14 | OpenAI가 `openai/math` 저장소에 "VP and VNP are different" 추가 |
| 11월 24~25일 | OpenAI가 수학 원고 9편을 추가로 공개하며, 그중 두 편이 VP/VNP 결과를 포함한다고 설명 (4탄에서 다룹니다) |

### Anthropic(Claude)이 공개한 것

논문은 70쪽이고, 저자는 "Claude (Anthropic)"로 적혀 있습니다. README에는 이 결과가 **Anthropic 내부 연구용 Claude 모델이 발견했고, 아직 사람 수학자가 증명을 확인하지 않았다** 고 명시되어 있습니다.

| 항목 | 내용 |
|----|----|
| 주장 | 모든 체(field)에서 VP ≠ VNP |
| 하한 | 해밀턴 회로 다항식(모든 체)과 퍼머넌트(표수 2 제외)에 2<sup>Ω((log m)<sup>4/3</sup>)</sup> 크기의 회로 하한, 근사 회로까지 확장 |
| Lean 규모 | 파일 324개, 약 72,932줄 (Lilting 집계), Lean 4.33.1 |
| 사용 공리 | `propext`, `Classical.choice`, `Quot.sound` 세 개뿐 |
| CI 검사 | 독립 검사기(Comparator, nanoda) 통과 보고 |

### OpenAI가 공개한 것

OpenAI의 "VP and VNP are different"는 저자를 "OpenAI"로 적었고, DataStudios에 따르면 약 30쪽입니다. Lean으로는 모든 체에서의 정확한 분리(해밀턴 회로 다항식, 표수 2를 제외한 퍼머넌트)를 다루고, 경계(border) 회로에 대한 하한 exp(Ω((log n)<sup>5/4</sup>))는 논문 쪽 주장입니다. OpenAI는 자기 원고들을 "날것의 연구 데이터"라고 부르며, Lean이 없는 부분에는 "문제가 있을 수 있다"고 적었습니다.

📌 두 증명은 얼마나 닮았나

Scott Aaronson은 두 증명이 모두 "압축(compression)과 대각선 논법(diagonalization)"을 쓴다는 점에서 비슷해 보인다고 평가했습니다. 하한의 지수는 Anthropic 쪽이 4/3, OpenAI 쪽이 5/4로, Maccus는 Anthropic의 하한이 더 강하다고 정리했습니다.

### Lean은 무엇을 확인했고, 무엇을 못 했나

Lean 증명이 통과했다는 것은 "적어 둔 정의에서 적어 둔 결론이 논리적으로 나온다"는 뜻입니다. 남은 빈칸은 **정의가 맞느냐** 입니다. Anthropic 쪽에서 VP, VNP, 퍼머넌트, 해밀턴 회로 다항식을 정의한 `Statement.lean`은 98줄인데, 이 정의가 논문과 수학계의 정의와 일치하는지는 기계로 검사되지 않습니다. Lilting의 분석에 따르면 논문 부록 Q는 이 일치를 **다른 AI가 확인했다** 고 적고 있습니다.

▶ Lean 증명을 직접 검사할 때 쓰는 기본 흐름 (예시)

```
# 1. 저장소 받기
git clone https://github.com/anthropics/formal-math.git
cd formal-math/vp-vnp

# 2. 고정된 Lean/Mathlib 버전으로 전체 빌드 (오류 없이 끝나야 합니다)
lake exe cache get     # Mathlib 미리 빌드된 파일 받기
lake build

# 3. 핵심 정리가 어떤 공리에 기대는지 확인 (Lean 파일 안에서)
#    #print axioms 정리_이름
#    → [propext, Classical.choice, Quot.sound] 만 나와야 '숨은 가정' 없음
```

### 전문가 반응

| 전문가 | 반응 |
|----|----|
| Lance Fortnow | Anthropic 결과를 "올해 가장 중요한 계산복잡도 결과"라고 불렀고(Maccus 보도), 형식화를 Claude와 Gemini로 검토한 뒤 맞을 가능성이 높다고 봤습니다. 다만 P vs NP는 여전히 손이 닿지 않는다고 했습니다. |
| Scott Aaronson | Lean 증명은 학술지 논문보다 높은 기준을 만족한다고 평가했고, 자신의 P ≠ NP 확신도를 95%에서 96%로 올렸다고 밝혔습니다. |

2026년 11월 26일 기준으로 두 논문 모두 사람이 한 줄씩 검토한 결과는 공개되지 않았습니다.

## 03 VP ≠ VNP와 P ≠ NP는 무엇이 다를까

**한 줄 요약:** 이번 결과는 P vs NP의 '대수 버전'을 푼 것이지, 100만 달러가 걸린 P vs NP 자체를 푼 것은 아닙니다.

| 비교 | VP vs VNP | P vs NP |
|----|----|----|
| 계산 모델 | 덧셈·곱셈 게이트만 쓰는 대수 회로 | AND/OR/NOT 같은 불리언 회로, 튜링 기계 |
| 무엇을 계산하나 | 다항식 그 자체 (모든 입력에서 같은 식이어야 함) | 0/1 입력에 대한 정답만 맞으면 됨 |
| 대표 문제 | 퍼머넌트, 해밀턴 회로 다항식 | SAT, 외판원 문제, 해밀턴 회로 찾기 |
| 제시 | 발리언트, 1979 | 쿡·레빈, 1971 |
| 상금 | 없음 | 클레이 밀레니엄 문제 100만 달러 |
| 2026년 11월 상태 | AI 증명 2건 공개, 사람 검토 전 | 미해결 |

불리언 회로는 0과 1에서 답만 맞으면 되므로, 대수 회로가 쓸 수 없는 '꼼수'를 쓸 수 있습니다. 그래서 대수 회로에서 불가능하다는 것을 보여도 불리언 회로에서까지 불가능하다는 결론은 나오지 않습니다. 계산복잡도 학계에서 VP vs VNP를 P vs NP로 가는 길목의 더 다루기 쉬운 문제로 봐 온 이유입니다.

## 04 앞으로 벌어질 일

**한 줄 요약:** 결과가 확인되면 계산복잡도의 '하한 증명'에 새 길이 열리고, AI 연구소 사이의 '최초' 경쟁과 검증 방식도 함께 주목받게 됩니다.

### 1. 하한 증명 기술의 확산

Aaronson이 짚은 것처럼 두 증명이 모두 압축과 대각선 논법을 쓴다면, 이 기법이 다른 하한 문제에도 쓰일 수 있는지가 다음 질문이 됩니다. 실제로 OpenAI는 11월 24일 공개한 원고 중 두 편("Paths, trees and grids separate Valiant's hierarchy", "Circuit lower bounds for Hamiltonian cycle and the permanent")이 VP/VNP 결과를 포함하는 더 넓은 결과라고 설명했습니다.

### 2. "누가 먼저인가"의 문제

Anthropic은 공개 시각이 먼저였고, OpenAI는 결과를 얻은 날짜가 17일 먼저라고 기록했습니다. 사람 수학자 사이에서는 보통 먼저 공개한 쪽을 우선으로 인정해 왔지만, AI 연구소가 내부에 결과를 쌓아 두고 있다가 공개하는 상황은 새로운 형태입니다.

### 3. 증명 검증 방식의 변화

이번 사례에서는 Lean이 논리를 검사하고, 정의 일치는 다른 AI가 확인하고, 마지막으로 사람이 읽는 순서가 생겼습니다. "학술지 동료 심사"만이 기준이던 수학에서, 기계 검증을 어디까지 인정할지에 대한 논의가 본격적으로 시작될 수 있습니다.

🔥 핵심

이번 결과의 의미는 "AI가 단순히 계산을 대신한 것이 아니라, 수십 년 동안 사람이 못 찾은 증명 아이디어를 냈다"는 데 있습니다. 동시에 그 증명을 사람이 아직 다 확인하지 못했다는 점도 함께 기억해야 합니다.

## 정리

**문제:** 행렬식과 퍼머넌트처럼 생김새는 같고 계산 난이도는 다른 다항식이 정말 다른 부류인지 묻는 1979년 난제입니다.

**AI가 한 일:** 2026년 11월 23일 Anthropic(Claude)이, 약 4시간 뒤 OpenAI가 각각 Lean 증명과 함께 VP ≠ VNP를 발표했습니다.

**지금 상태:** 기계 검사 통과는 보고되었지만 정의 일치와 사람의 전체 검토는 남아 있고, P ≠ NP와는 다른 문제입니다.

✦ 지금 해볼 것

☐ 위 파이썬 코드로 행렬식과 퍼머넌트 계산 시간 차이를 직접 확인해 보기

☐ `anthropics/formal-math`의 `vp-vnp` 폴더 README 읽어 보기

☐ 4탄에서 OpenAI가 하루에 올린 9편과 VP/VNP의 관계 이어서 보기

## 자주 묻는 질문

### VP ≠ VNP가 증명되면 P ≠ NP도 증명된 건가요?

아닙니다. VP ≠ VNP는 덧셈과 곱셈만 쓰는 대수 회로에서의 분리이고, P ≠ NP는 불리언 회로와 튜링 기계에서의 분리입니다. Lance Fortnow도 이번 결과를 높이 평가하면서 P vs NP는 여전히 손이 닿지 않는다고 말했습니다.

### Claude와 OpenAI 중 누가 먼저 증명했나요?

공개는 Anthropic이 먼저입니다. Anthropic은 2026년 11월 23일 20:04(UTC)에, OpenAI는 약 4시간 뒤인 11월 24일 01:14(UTC)에 공개했습니다. 다만 OpenAI는 결과를 11월 6일에 얻었다고 기록했습니다.

### 이 증명은 검증이 끝났나요?

Lean 검사는 통과했다고 보고되었고, 표준 공리 세 개만 썼습니다. 하지만 정의가 수학계의 정의와 맞는지는 기계 검사 밖이고, 2026년 11월 26일 기준 사람의 전체 검토와 동료 심사는 나오지 않았습니다.

## 참고 링크

[Anthropic · formal-math 저장소 ↗](https://github.com/anthropics/formal-math) [OpenAI · math 저장소 ↗](https://github.com/openai/math) [Lilting · Lean 증명 분석 ↗](https://lilting.ch/en/articles/vp-vnp-valiant-conjecture-claude-lean) [DataCamp · Claude의 발리언트 추측 증명 ↗](https://www.datacamp.com/blog/claude-claims-proof-of-valiants-conjecture-vp-vs-vnp) [Maccus · OpenAI 증명과 타임라인 ↗](https://maccus.fr/en/openai-vp-vs-vnp-proof/) [Wikipedia · VP vs VNP ↗](https://en.wikipedia.org/wiki/VP_vs._VNP_problem)

---

`#VPVNP` `#발리언트추측` `#계산복잡도` `#PvsNP` `#퍼머넌트` `#Claude` `#OpenAI` `#Lean` `#AI수학` `#AI심층분석`
