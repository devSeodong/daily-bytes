---
title: "오늘의 CS/개발 이슈 (2026.11.24) - .NET 8 지원 종료, PostgreSQL 14 EOL, 지금 무엇을 해야 할까"
date: 2026-11-24
category: "개발 이슈"
tistory: https://dongseodong.tistory.com/61
tags: ["angular", "EOL", "NET10", "NET8", "pg_upgrade", "PostgreSQL", "개발이슈", "버전업그레이드", "보안패치", "지원종료"]
cover: assets/2026-11-24-dotnet8-postgresql14-eol.jpg
---
# 오늘의 CS/개발 이슈 (2026.11.24) - .NET 8 지원 종료, PostgreSQL 14 EOL, 지금 무엇을 해야 할까

> 🛠️ **개발 이슈** · 2026-11-24 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/61)

![대표 이미지](assets/2026-11-24-dotnet8-postgresql14-eol.jpg)

11월은 지원 종료(EOL)가 몰린 달이에요. 특히 **.NET 8·9, PostgreSQL 14, Angular 20** 은 쓰는 곳이 많아서 영향이 커요. 오늘은 EOL이 정확히 뭘 의미하는지 짚고, 이 세 가지를 **무슨 일이 있었는지, 지원 정책은 어떻게 되는지, 실제로 어떤 명령으로 올리면 되는지** 까지 정리해 볼게요.

TL;DR · 한눈에 보기

1 **.NET 8(LTS)·.NET 9(STS)** 가 11월 10일 함께 끝났어요. .NET 10 LTS(2028년 11월까지)로 올리는 게 정답이에요.

2 **PostgreSQL 14** 는 11월 12일 14.25를 마지막으로 EOL. 지원 버전은 15~19이고, pg_upgrade로 빠르게 올릴 수 있어요.

3 **Angular 20** 은 11월 28일 LTS가 끝나요. 메이저는 한 단계씩, 20 → 21 → 22 순서로 올려야 해요.

| 날짜         | 종료 대상                          | 다음 행선지                     |
|--------------|------------------------------------|---------------------------------|
| 11/1         | Alpine Linux 3.21, OpenSSL 3.6     | 최신 Alpine / OpenSSL LTS       |
| 11/7         | Ruby on Rails 8.0 보안 지원        | Rails 8.1                       |
| 11/10        | .NET 8, .NET 9, PowerShell 7.4·7.5 | .NET 10 LTS, PowerShell 7.6 LTS |
| 11/12        | PostgreSQL 14                      | PostgreSQL 18 또는 19           |
| 11/28 (예정) | Angular 20 LTS                     | Angular 21 → 22                 |
| 12/1 (예정)  | Redis 8.0                          | 최신 Redis                      |
| 12/31 (예정) | PHP 8.2 보안 지원                  | PHP 8.4 이상                    |

목차

[EOL은 정확히 무슨 의미일까](#s0)

[1. .NET 8·9 지원 종료 → .NET 10으로](#s1)

[2. PostgreSQL 14 EOL → pg_upgrade로 올리기](#s2)

[3. Angular 20 LTS 종료 → 한 단계씩](#s3)

[정리](#s-sum)

## EOL은 정확히 무슨 의미일까

EOL(End of Life)이 지나도 프로그램은 그대로 돌아가요. 문제는 **보안 패치가 더 이상 나오지 않는다** 는 거예요. 새 취약점이 발견돼도 고쳐지지 않으니 시간이 갈수록 위험해지고, 보안 심사나 클라우드 런타임 정책에서도 하나둘 막히기 시작해요.

> EOL은 "멈추는 날"이 아니라 "혼자 남겨지는 날"이에요.

## 01 .NET 8·9 지원 종료 → .NET 10으로

### 무슨 일이 있었나

11월 10일 .NET 11(STS)이 정식 출시되면서, 같은 날 **.NET 8과 .NET 9가 함께 지원 종료** 됐어요. .NET 8의 마지막 패치는 8.0.34예요. 같은 날 PowerShell 7.4·7.5도 끝나서, PowerShell은 7.6 LTS로 옮기면 돼요.

### 배경: 왜 두 버전이 한꺼번에 끝났나

.NET은 매년 11월에 새 메이저가 나오고, 짝수 버전은 **LTS(3년)** , 홀수 버전은 **STS(2년)** 지원을 받아요. 2023년 11월에 나온 .NET 8(LTS)은 3년을, 2024년 11월에 나온 .NET 9(STS)는 2년을 채워서 같은 날 끝난 거예요.

| 버전    | 종류 | 지원 종료                     |
|---------|------|-------------------------------|
| .NET 8  | LTS  | 2026-11-10 (종료)             |
| .NET 9  | STS  | 2026-11-10 (종료)             |
| .NET 10 | LTS  | 2028-11-14                    |
| .NET 11 | STS  | 2028년 11월 (출시 2026-11-10) |

### 영향: 클라우드 런타임도 따라와요

AWS Lambda는 **dotnet8 런타임** 을 2026년 11월 10일부로 deprecated 처리했어요. 바로 멈추지는 않지만 일정이 잡혀 있어요.

| 일정       | Lambda dotnet8에 생기는 일            |
|------------|---------------------------------------|
| 2026-11-10 | 지원 중단(deprecated), 보안 패치 없음 |
| 2027-07-29 | dotnet8으로 새 함수 생성 차단         |
| 2027-08-31 | 기존 함수 업데이트도 차단             |

### 대응 방안

STEP 1

현재 런타임과 SDK 버전 확인

STEP 2

TargetFramework를 net10.0으로 변경

STEP 3

NuGet 패키지 업데이트 후 빌드·테스트

STEP 4

Docker 이미지, CI SDK, Lambda 런타임 같이 올리기

▶ 설치된 런타임·SDK 확인하고 패키지 점검하기

```
dotnet --list-runtimes
dotnet --list-sdks

# 오래된 NuGet 패키지 목록
dotnet list package --outdated
```

▶ 프로젝트 파일(.csproj) 수정

```
<PropertyGroup>
  <!-- 변경 전: net8.0 -->
  <TargetFramework>net10.0</TargetFramework>
</PropertyGroup>
```

▶ Docker 베이스 이미지도 함께

```
# 변경 전: mcr.microsoft.com/dotnet/aspnet:8.0
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

📌 8 → 10? 8 → 11?

.NET 11은 STS라 2년 뒤면 또 올려야 해요. 운영 서비스라면 3년 지원되는 **.NET 10 LTS** 를 고르는 게 일반적이에요. 마이그레이션 전에 공식 문서의 "호환성이 깨지는 변경(breaking changes)" 목록을 꼭 훑어보세요.

💡 왜 중요할까

.NET 8은 지난 3년간 가장 널리 쓰인 LTS였어요. 그래서 이번 EOL은 **엔터프라이즈 백엔드, 사내 도구, 서버리스 함수** 까지 한꺼번에 걸려요. 보안 감사에서 "지원 종료 런타임"으로 지적받기 전에 일정을 잡아 두는 게 좋아요.

[출처 · .NET 지원 정책 ↗](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core) [출처 · PowerShell 수명 주기 ↗](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle) [출처 · AWS Lambda 런타임 ↗](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)

------------------------------------------------------------------------

## 02 PostgreSQL 14 EOL → pg_upgrade로 올리기

### 무슨 일이 있었나

PostgreSQL 14는 11월 12일 **14.25** 를 마지막 마이너 릴리스로 지원이 끝났어요. 일주일 뒤인 11월 19일에는 PostgreSQL 19가 정식 출시됐고요. 지금 지원되는 버전은 **15, 16, 17, 18, 19** 예요.

### 배경: 5년 지원 정책

PostgreSQL은 메이저 버전마다 약 5년간 버그·보안 수정을 내요. 14는 2021년에 나왔으니 정확히 5년을 채운 거예요. 마이너 업그레이드(14.24 → 14.25)는 바이너리만 바꾸면 되지만, **메이저 업그레이드는 데이터 파일 형식이 달라서** 별도 절차가 필요해요.

### 업그레이드 방법 비교

| 방법                                 | 속도·다운타임           | 이럴 때                                     |
|--------------------------------------|-------------------------|---------------------------------------------|
| pg_dump / pg_restore                 | DB 크기에 비례해 길어요 | 작은 DB, 가장 단순하고 안전하게             |
| pg_upgrade (기본 복사)               | 빠름                    | 중대형 DB, 디스크 여유가 있을 때            |
| pg_upgrade --link / --clone / --swap | 매우 빠름               | 큰 DB. 단, --link는 롤백이 어려워 백업 필수 |
| 논리 복제                            | 다운타임 최소           | 24시간 서비스, 설정 복잡도 감수 가능할 때   |

### 대응 방안: pg_upgrade 실전 순서

STEP 1

새 버전(예: 18) 설치 후 initdb

STEP 2

--check로 사전 점검

STEP 3

기존 서버 중지 후 실제 업그레이드

STEP 4

통계 재수집 후 새 서버로 전환

▶ 1) 사전 점검 (데이터는 건드리지 않아요)

```
pg_upgrade \
  -b /usr/lib/postgresql/14/bin \
  -B /usr/lib/postgresql/18/bin \
  -d /etc/postgresql/14/main \
  -D /etc/postgresql/18/main \
  --check
```

▶ 2) 실제 업그레이드 (--link는 빠르지만 백업 필수, -j는 병렬 작업 수)

```
pg_upgrade \
  -b /usr/lib/postgresql/14/bin \
  -B /usr/lib/postgresql/18/bin \
  -d /etc/postgresql/14/main \
  -D /etc/postgresql/18/main \
  --link -j 4
```

▶ 3) 업그레이드 후 통계 재수집

```
# 빠진 통계부터 단계적으로 채우고
vacuumdb --all --analyze-in-stages --missing-stats-only
# 이어서 전체 통계를 갱신해요
vacuumdb --all --analyze-only
```

⚠ 놓치기 쉬운 것

업그레이드 직후엔 플래너 통계가 비어 있어서 쿼리가 갑자기 느려질 수 있어요. 위 3번 단계를 빼먹지 마세요. AWS RDS·Aurora 같은 관리형 DB라면 콘솔의 메이저 버전 업그레이드를 쓰되, **스냅샷을 먼저** 떠 두세요.

💡 왜 중요할까

DB는 한 번 올리면 쉽게 되돌리기 어려운 인프라라서 "나중에"가 가장 많이 미뤄지는 곳이에요. 14에서 바로 18·19로 가면 **앞으로 4~5년은 걱정 없이** 쓸 수 있으니, 이번 EOL을 한 번에 크게 건너뛸 기회로 쓰는 게 좋아요.

[출처 · PostgreSQL 버전 정책 ↗](https://www.postgresql.org/support/versioning/)

------------------------------------------------------------------------

## 03 Angular 20 LTS 종료 → 한 단계씩

### 무슨 일이 있나

Angular 20은 이번 주 금요일, **11월 28일에 LTS가 끝나요.** 지금 Angular 21은 LTS 기간(2027년 6월까지)이고, 6월 3일에 나온 Angular 22가 활성 지원 중이에요.

### 배경: 24개월 지원 주기

Angular는 약 6개월마다 메이저 버전을 내고, 각 버전을 **총 24개월** 지원해요. 처음 12개월은 기능 업데이트와 버그 수정이 나오는 활성 지원, 이후 12개월은 치명적 버그와 보안 수정만 나오는 LTS예요.

| 버전       | 상태                        | 지원 종료    |
|------------|-----------------------------|--------------|
| Angular 20 | LTS                         | 2026-11-28   |
| Angular 21 | LTS                         | 2027년 6월   |
| Angular 22 | 활성 지원 (2026-06-03 출시) | 2028년 6월경 |

### 대응 방안

가장 중요한 규칙은 **메이저 버전을 건너뛰지 않는 것** 이에요. ng update는 한 번에 한 메이저씩만 올리도록 되어 있고, 그때마다 코드 마이그레이션 스크립트가 자동으로 같이 돌아요.

STEP 1

Git 작업 트리 깨끗하게 정리

STEP 2

20 → 21 업데이트 후 빌드·테스트

STEP 3

21 → 22 업데이트 후 빌드·테스트

STEP 4

서드파티 라이브러리 호환 버전 확인

▶ 20에서 22까지 한 단계씩 올리기

```
# 현재 버전 확인
ng version

# 1단계: 20 → 21
ng update @angular/core@21 @angular/cli@21
npm test && ng build
git commit -am "chore: angular 21"

# 2단계: 21 → 22
ng update @angular/core@22 @angular/cli@22
npm test && ng build
```

📌 팁

Angular Material 같은 공식 패키지도 같이 올려야 해요(예: `ng update @angular/material@21`). [Angular 업데이트 가이드](https://angular.dev/update-guide)에서 현재 버전과 목표 버전을 고르면 해야 할 일을 체크리스트로 보여줘요.

💡 왜 중요할까

프런트엔드는 의존성이 많아서 버전이 두세 단계 밀리면 한 번에 따라잡기가 급격히 어려워져요. LTS가 끝나는 지금 **한 단계라도 올려 두면** 이후 업그레이드 비용이 크게 줄어요.

[출처 · Angular 릴리스 정책 ↗](https://angular.dev/reference/releases) [출처 · Angular 업데이트 가이드 ↗](https://angular.dev/update-guide)

## 그 밖의 소식

[**Ruby on Rails 8.0 보안 지원 종료** 11/7, 8.1로 업그레이드 · Rails ↗](https://rubyonrails.org/maintenance)[**Alpine 3.21 · OpenSSL 3.6 EOL** 11/1, 컨테이너 베이스 이미지 점검 · Alpine ↗](https://alpinelinux.org/releases/)[**Redis 8.0 EOL 예정** 12/1 · Redis ↗](https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/)[**PHP 8.2 보안 지원 종료 예정** 12/31 · PHP ↗](https://www.php.net/supported-versions.php)[**11월 EOL 전체 타임라인** 한눈에 보기 · endoflife.date ↗](https://endoflife.date/timeline/2026/11/)

## 정리

**.NET:** 8·9가 끝났어요. 운영 서비스는 .NET 10 LTS(2028-11-14까지)로, Lambda dotnet8은 2027년 7월 전에 옮기세요.

**PostgreSQL:** 14는 EOL, 지원은 15~19. pg_upgrade --check부터 해 보고, 끝나면 vacuumdb로 통계를 채우세요.

**Angular:** 20 LTS가 11/28 종료. 24개월 주기, ng update로 한 메이저씩 올려요.

✦ 지금 해볼 것

☐ dotnet --list-runtimes로 서버마다 .NET 8·9가 남아 있는지 확인하기

☐ PostgreSQL 14 서버에서 pg_upgrade --check 한 번 돌려 보기

☐ Angular 프로젝트에서 ng version 확인하고 21 업데이트 브랜치 만들기

---

`#angular` `#EOL` `#NET10` `#NET8` `#pg_upgrade` `#PostgreSQL` `#개발이슈` `#버전업그레이드` `#보안패치` `#지원종료`
