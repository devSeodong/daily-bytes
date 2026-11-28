---
title: "로드밸런서 종류 정리 - OSI 7계층으로 이해하는 L2·L3·L4·L7 로드밸런서와 부하 분산 알고리즘"
date: 2026-11-28
category: "Computer Science"
tistory: https://dongseodong.tistory.com/85
tags: ["로드밸런서", "LoadBalancer", "L4로드밸런서", "L7로드밸런서", "OSI7계층", "부하분산", "Nginx", "HAProxy", "AWSALB", "ComputerScience"]
cover: assets/2026-11-28-load-balancer-types-osi.png
---
# 로드밸런서 종류 정리 - OSI 7계층으로 이해하는 L2·L3·L4·L7 로드밸런서와 부하 분산 알고리즘

> 💻 **Computer Science** · 2026-11-28 · 📝 [티스토리에서 보기](https://dongseodong.tistory.com/85)

![대표 이미지](assets/2026-11-28-load-balancer-types-osi.png)

서비스 사용자가 늘면 서버 한 대로는 버틸 수 없어서 여러 대로 나누게 되고, 이때 요청을 골고루 나눠 주는 장치가 **로드밸런서** (Load Balancer)입니다. 그런데 로드밸런서를 고르다 보면 L4, L7, NLB, ALB 같은 용어가 쏟아지고, 무엇이 어떻게 다른지 헷갈리기 쉽습니다.

이 글에서는 로드밸런서의 종류를 **OSI 7계층 기준** 으로 정리합니다. "몇 계층 정보까지 보고 판단하느냐"가 곧 로드밸런서의 종류이기 때문입니다. 계층 개념이 처음이라면 먼저 아래 글을 읽고 오시면 훨씬 쉽게 이해됩니다.

✦ 먼저 읽으면 좋은 글

[OSI 7계층 완벽 정리 - 택배 비유로 이해하는 계층별 역할, 프로토콜, 장비, 캡슐화](https://dongseodong.tistory.com/84)

TL;DR · 한눈에 보기

1 로드밸런서의 종류는 **요청의 어느 계층 정보까지 보고 서버를 고르느냐** 로 나뉩니다. L2는 MAC, L3는 IP, L4는 IP와 포트, L7은 URL·헤더·쿠키 같은 내용까지 봅니다.

2 실무에서 가장 많이 쓰는 것은 빠르고 단순한 **L4** 와, 경로별 라우팅·TLS 종료가 가능한 **L7** 입니다. AWS로 치면 NLB가 L4, ALB가 L7, GWLB가 L3입니다.

3 계층과 별개로 **분산 알고리즘** (라운드 로빈, 최소 연결, IP 해시 등)과 **헬스 체크** , **세션 유지** 를 함께 정해야 제대로 동작합니다.

목차

[1. 로드밸런서란 무엇이고 왜 필요한가](#s1)

[2. OSI 계층별 로드밸런서 한눈에 보기](#s2)

[3. L2 로드밸런싱: MAC 주소로 나누기](#s3)

[4. L3 로드밸런싱: IP 주소로 나누기](#s4)

[5. L4 로드밸런서: IP와 포트로 나누기](#s5)

[6. L7 로드밸런서: 내용을 보고 나누기](#s6)

[7. L4와 L7 로드밸런서 비교](#s7)

[8. 부하 분산 알고리즘](#s8)

[9. 헬스 체크와 세션 유지](#s9)

[10. DNS 로드밸런싱과 GSLB](#s10)

[11. 클라우드 로드밸런서 고르기](#s11)

[12. 직접 해보기: Docker로 L7 로드밸런서 만들기](#s12)

## 01 로드밸런서란 무엇이고 왜 필요한가

**한 줄 답:** 로드밸런서는 클라이언트와 여러 서버 사이에 서서, 들어오는 요청을 정해진 규칙에 따라 여러 서버로 나눠 보내는 장치 또는 소프트웨어입니다. 목적은 **성능 확장, 장애 대비, 무중단 배포** 입니다.

### 스케일 업과 스케일 아웃

| 방식 | 방법 | 장점 | 한계 |
|----|----|----|----|
| 스케일 업 | 서버 한 대의 CPU·메모리를 키웁니다. | 구조가 단순합니다. | 장비 성능에 상한이 있고, 그 한 대가 죽으면 서비스 전체가 멈춥니다. |
| 스케일 아웃 | 비슷한 서버를 여러 대 둡니다. | 필요한 만큼 늘릴 수 있고, 한 대가 죽어도 나머지가 처리합니다. | 요청을 나눠 줄 **로드밸런서** 가 필요합니다. |

### 로드밸런서가 해 주는 일

부하 분산

요청을 여러 서버로 나눠 한 서버에 몰리지 않게 합니다.

헬스 체크

주기적으로 서버 상태를 확인하고, 응답이 없는 서버는 자동으로 빼 둡니다.

무중단 배포

서버를 한 대씩 빼고 새 버전을 올린 뒤 다시 넣어, 사용자는 중단을 느끼지 않습니다.

단일 진입점

사용자는 로드밸런서 주소 하나만 알면 되고, 뒤의 서버 구성은 숨겨집니다.

### 택배 비유로 보면

이전 글의 택배 비유를 이어 보면, 로드밸런서는 **물류센터의 분류 담당자** 입니다. 상자에 붙은 정보 중 무엇을 보고 분류하느냐에 따라 일하는 방식이 달라집니다.

| 분류 담당자가 보는 것                       | 계층  | 로드밸런서    |
|---------------------------------------------|-------|---------------|
| 구간 송장(MAC)만 보고 다음 트럭에 싣기      | 2계층 | L2 로드밸런싱 |
| 목적지 주소(IP)만 보고 나누기               | 3계층 | L3 로드밸런싱 |
| 주소와 "몇 호(포트)"까지 보고 나누기        | 4계층 | L4 로드밸런서 |
| 상자를 열어 내용물(URL, 쿠키)을 보고 나누기 | 7계층 | L7 로드밸런서 |

상자를 열어 볼수록 더 똑똑하게 나눌 수 있지만, 그만큼 시간이 더 걸립니다. 이것이 L4와 L7의 차이를 이해하는 핵심입니다.

## 02 OSI 계층별 로드밸런서 한눈에 보기

**한 줄 답:** 계층 번호가 높을수록 더 많은 정보를 보고 정교하게 나눌 수 있지만, 처리 비용이 커집니다.

L7 응용 URL 경로, 호스트 이름, 헤더, 쿠키, 메서드 → **ALB, Nginx, HAProxy(http), Envoy**

L5·L6 단독 로드밸런서 분류로는 거의 쓰지 않습니다 (TLS 처리는 L4·L7 장비가 함께 합니다)

L4 전송 출발·도착 IP + 포트 + 프로토콜(TCP/UDP) → **NLB, LVS(IPVS), HAProxy(tcp), Nginx stream**

L3 네트워크 IP 주소 → **ECMP 라우팅, Anycast, AWS GWLB**

L2 데이터링크 MAC 주소 → **DSR(MAC 변경 방식), 링크 묶음(LACP)**

| 구분 | 판단 기준 | 대표 예 | 장점 | 단점 |
|----|----|----|----|----|
| L2 | MAC 주소 | DSR(Direct Routing), LACP | 매우 빠름, IP를 바꾸지 않음 | 같은 2계층 네트워크 안에서만 가능, 기능이 거의 없음 |
| L3 | IP 주소 | ECMP, Anycast, AWS GWLB | 라우터 수준 속도, 대규모 트래픽 | 포트나 내용으로 나눌 수 없음 |
| L4 | IP + 포트 (5-튜플) | AWS NLB, LVS/IPVS, HAProxy tcp 모드 | 빠름, TCP·UDP 모두 가능, 프로토콜 무관 | URL·쿠키 기반 분기 불가 |
| L7 | URL, 헤더, 쿠키 등 | AWS ALB, Nginx, HAProxy http 모드, Envoy | 경로별 라우팅, TLS 종료, 캐싱, 보안 기능 | 상대적으로 느리고 자원을 많이 씀 |
| DNS(GSLB) | DNS 응답 | Route 53, Cloudflare Load Balancing | 지역·데이터센터 단위 분산 | DNS 캐시 때문에 즉시 반영되지 않음 |

## 03 L2 로드밸런싱: MAC 주소로 나누기

**한 줄 답:** L2 방식은 IP 패킷은 그대로 두고, 프레임의 **도착 MAC 주소만 실제 서버의 MAC으로 바꿔** 보내는 방식입니다. 대표적인 것이 DSR(Direct Server Return)의 MAC 변경 방식이며, 독립 장비 분류라기보다 L4 로드밸런서의 **전달 방식** 중 하나로 많이 씁니다.

### 동작 원리

① 요청

클라이언트가 가상 IP(VIP)로 요청을 보냅니다.

② MAC 교체

로드밸런서가 서버를 고른 뒤 도착 MAC만 그 서버의 MAC으로 바꿉니다. 도착 IP는 여전히 VIP입니다.

③ 서버 처리

서버는 루프백(lo)에 VIP를 갖고 있어 자기 패킷으로 받아들입니다.

④ 직접 응답

응답은 로드밸런서를 거치지 않고 서버가 클라이언트에게 바로 보냅니다.

응답 트래픽은 보통 요청보다 훨씬 큽니다(작은 요청, 큰 영상 응답). DSR은 이 큰 응답이 로드밸런서를 지나지 않으므로 로드밸런서 부담이 크게 줄어듭니다. 대신 로드밸런서와 서버가 **같은 2계층 네트워크** (같은 스위치, 같은 VLAN)에 있어야 하고, 서버마다 ARP 설정을 따로 해야 합니다.

▶ LVS(IPVS)로 DSR 구성하기 예시 (Linux, 가상 IP 10.0.0.100)

```
# 로드밸런서: 가상 서비스 생성, 라운드 로빈(rr)
sudo ipvsadm -A -t 10.0.0.100:80 -s rr
# -g = gatewaying = DSR(MAC 변경) 방식으로 실제 서버 추가
sudo ipvsadm -a -t 10.0.0.100:80 -r 10.0.0.11:80 -g
sudo ipvsadm -a -t 10.0.0.100:80 -r 10.0.0.12:80 -g

# 실제 서버(각각): VIP를 루프백에 두고, 이 VIP에 대한 ARP 응답은 하지 않음
sudo ip addr add 10.0.0.100/32 dev lo
sudo sysctl -w net.ipv4.conf.all.arp_ignore=1
sudo sysctl -w net.ipv4.conf.all.arp_announce=2
```

📌 링크 묶음(LACP)도 2계층 분산입니다

스위치와 서버 사이 랜선 여러 개를 하나처럼 묶는 링크 묶음(IEEE 802.1AX, LACP)은 프레임을 여러 선으로 나눠 보내는 2계층 분산 기술입니다. 서버 사이의 분산은 아니지만 "L2에서도 부하를 나눈다"는 예로 알아 두면 좋습니다.

## 04 L3 로드밸런싱: IP 주소로 나누기

**한 줄 답:** L3 방식은 라우터 수준에서 **IP 주소와 경로** 만 보고 트래픽을 나눕니다. 대표적으로 같은 비용의 경로 여러 개에 나눠 보내는 **ECMP** , 같은 IP를 여러 지역에서 광고하는 **Anycast** 가 있습니다.

| 기술 | 동작 | 어디서 쓰나 |
|----|----|----|
| ECMP (Equal-Cost Multi-Path) | 목적지까지 비용이 같은 경로가 여러 개면, 패킷 헤더를 해시해서 경로를 고릅니다. 같은 연결은 같은 경로로 가도록 해시합니다. | 데이터센터 라우터, 여러 대의 L4 로드밸런서 앞단 |
| Anycast | 여러 지역 서버가 같은 IP를 BGP로 알리면, 사용자는 네트워크상 가장 가까운 곳으로 연결됩니다. | CDN, 공용 DNS(예: 1.1.1.1, 8.8.8.8) |
| AWS Gateway Load Balancer | 3계층에서 IP 패킷을 GENEVE(6081 포트)로 감싸 방화벽·침입 탐지 같은 보안 장비 묶음에 나눠 보냅니다. | 서드파티 보안 장비를 여러 대 운영할 때 |

대형 서비스는 보통 **ECMP(L3) → 여러 대의 L4 로드밸런서 → L7 로드밸런서 → 서버** 처럼 계층을 쌓아서 씁니다. 아래 계층이 빠르게 큰 덩어리로 나누고, 위 계층이 세밀하게 나누는 구조입니다.

## 05 L4 로드밸런서: IP와 포트로 나누기

**한 줄 답:** L4 로드밸런서는 TCP·UDP 헤더의 **IP 주소와 포트 번호** 를 보고 연결 단위로 서버를 고릅니다. 패킷 안의 내용(HTTP 등)은 보지 않으므로 빠르고, 어떤 TCP·UDP 프로토콜이든 처리할 수 있습니다.

### 연결 단위로 나눈다는 뜻

L4 로드밸런서는 새 TCP 연결(SYN)이 들어오면 서버 하나를 고르고, 그 연결의 5-튜플을 연결 테이블에 적어 둡니다. 이후 같은 연결의 패킷은 모두 같은 서버로 보냅니다. 그래서 하나의 TCP 연결 안에서 여러 HTTP 요청이 오가더라도(Keep-Alive, HTTP/2) **전부 같은 서버** 로 갑니다. 요청 단위로 나누려면 L7이 필요합니다.

### 전달 방식 세 가지

| 방식 | 요청 | 응답 | 특징 |
|----|----|----|----|
| NAT (프록시형 포함) | LB가 도착 IP를 서버 IP로 바꿈 | LB를 거쳐 돌아옴 | 구성이 쉽고 서버가 다른 네트워크에 있어도 됩니다. 응답도 LB를 지나서 LB 부담이 큽니다. |
| DSR (Direct Server Return) | MAC만 바꿈 (L2) 또는 터널 | 서버가 바로 응답 | LB 부담이 가장 적습니다. 같은 L2 네트워크 조건과 서버 설정이 필요합니다. |
| 터널 (IP-in-IP, GRE) | 원래 패킷을 새 IP로 감쌈 | 서버가 바로 응답 | DSR처럼 응답이 직접 가면서, 서버가 다른 네트워크에 있어도 됩니다. |

### 대표 제품과 설정 예

AWS의 **NLB** (Network Load Balancer), Linux 커널의 **LVS/IPVS** , **HAProxy** 의 `mode tcp`, **Nginx** 의 `stream` 모듈이 대표적인 L4 로드밸런서입니다. 데이터베이스, Redis, MQTT, 게임 서버처럼 HTTP가 아닌 트래픽을 나눌 때 특히 유용합니다.

▶ Nginx stream으로 MySQL 읽기 서버 L4 분산

```
# /etc/nginx/nginx.conf (http 블록 바깥에 stream 블록)
stream {
    upstream mysql_read {
        least_conn;                      # 연결 수가 가장 적은 서버로
        server 10.0.1.11:3306 max_fails=3 fail_timeout=10s;
        server 10.0.1.12:3306 max_fails=3 fail_timeout=10s;
    }
    server {
        listen 3306;                     # 4계층: 포트만 보고 전달
        proxy_pass mysql_read;
        proxy_connect_timeout 2s;
    }
}
```

▶ HAProxy tcp 모드 (haproxy.cfg)

```
frontend redis_in
    bind *:6379
    mode tcp                       # 내용을 해석하지 않는 L4 모드
    default_backend redis_nodes

backend redis_nodes
    mode tcp
    balance roundrobin
    option tcp-check               # TCP 연결로 헬스 체크
    server r1 10.0.2.11:6379 check
    server r2 10.0.2.12:6379 check
```

## 06 L7 로드밸런서: 내용을 보고 나누기

**한 줄 답:** L7 로드밸런서는 HTTP 같은 응용 계층 프로토콜을 해석해 **URL 경로, 호스트 이름, 헤더, 쿠키, 메서드** 를 보고 요청 단위로 서버를 고릅니다. 클라이언트와 TCP 연결을 끝까지 맺고(종료), 서버와는 새 연결을 맺는 **프록시** 방식으로 동작합니다.

### L7에서만 할 수 있는 일

| 기능 | 설명 | 예시 |
|----|----|----|
| 경로 기반 라우팅 | URL 경로에 따라 다른 서버 묶음으로 보냅니다. | `/api/*` → API 서버, `/static/*` → 정적 파일 서버 |
| 호스트 기반 라우팅 | `Host` 헤더로 도메인마다 다른 서비스로 보냅니다. | `shop.example.com`, `blog.example.com` |
| TLS 종료 | 로드밸런서가 HTTPS 암호를 풀고 서버에는 HTTP로 보냅니다. 인증서를 한 곳에서 관리합니다. | ALB에 ACM 인증서 연결 |
| 쿠키 기반 세션 유지 | 쿠키를 보고 같은 사용자를 같은 서버로 보냅니다. | 로그인 세션을 서버 메모리에 두는 옛 서비스 |
| 헤더 조작·리다이렉트 | `X-Forwarded-For`로 원래 클라이언트 IP 전달, HTTP → HTTPS 리다이렉트 | 301 리다이렉트 |
| 카나리·A/B 배포 | 요청의 일부(예: 5%)나 특정 헤더를 가진 요청만 새 버전으로 보냅니다. | 가중치 기반 대상 그룹 |
| 보안·캐싱·압축 | WAF 규칙, 요청 속도 제한, 응답 캐싱, gzip 압축 | SQL 인젝션 패턴 차단 |

### 대표 제품과 설정 예

AWS의 **ALB** (Application Load Balancer), **Nginx** 의 `http` 모듈, **HAProxy** 의 `mode http`, 서비스 메시에서 많이 쓰는 **Envoy** , 쿠버네티스의 **Ingress 컨트롤러** 가 L7 로드밸런서입니다.

▶ Nginx L7: 경로별 라우팅 + TLS 종료 + 원래 IP 전달

```
upstream api_servers {
    server 10.0.3.11:8080 weight=3;      # 성능 좋은 서버에 3배
    server 10.0.3.12:8080 weight=1;
    keepalive 32;                        # 서버 쪽 연결 재사용
}
upstream web_servers {
    server 10.0.4.11:3000;
    server 10.0.4.12:3000;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;
    ssl_certificate     /etc/ssl/example.com.crt;   # TLS 종료
    ssl_certificate_key /etc/ssl/example.com.key;

    location /api/ {                     # 7계층: URL 경로를 보고 분기
        proxy_pass http://api_servers;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location / {
        proxy_pass http://web_servers;
    }
}

server {                                 # HTTP → HTTPS 리다이렉트
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

⚠ L7 뒤의 서버에서 클라이언트 IP가 이상하게 보인다면

L7 로드밸런서는 클라이언트 대신 서버에 새 연결을 맺으므로, 서버 입장에서 출발 IP는 로드밸런서의 IP입니다. 실제 사용자 IP는 `X-Forwarded-For` 헤더로 전달되며, 애플리케이션(예: Spring의 `server.forward-headers-strategy`, Express의 `trust proxy`)에서 이 헤더를 믿도록 설정해야 접속 로그와 IP 차단이 제대로 동작합니다. L4 프록시에서 원래 IP가 필요하면 PROXY protocol을 씁니다.

## 07 L4와 L7 로드밸런서 비교

**한 줄 답:** 빠르고 단순하게 많은 연결을 나누려면 L4, URL·쿠키에 따라 똑똑하게 나누고 HTTPS를 한곳에서 처리하려면 L7을 씁니다. 둘을 함께 쓰는 구성도 흔합니다.

| 기준 | L4 로드밸런서 | L7 로드밸런서 |
|----|----|----|
| 보는 정보 | IP, 포트, 프로토콜 | URL, 호스트, 헤더, 쿠키, 메서드, 본문 |
| 분산 단위 | TCP 연결 (UDP는 흐름) | HTTP 요청 |
| 속도·자원 | 빠르고 가벼움 | 상대적으로 느리고 CPU를 더 씀 |
| TLS | 그대로 통과(패스스루)가 기본, 일부 제품은 종료도 지원 | 종료 후 내용 해석이 기본 |
| 프로토콜 | TCP·UDP 위의 모든 것 (DB, 게임, MQTT, gRPC 연결 단위) | HTTP/1.1, HTTP/2, HTTP/3, gRPC(요청 단위), WebSocket |
| 클라이언트 IP | NAT 없이 전달하면 서버가 그대로 봄 | `X-Forwarded-For`로 전달 |
| 대표 제품 | AWS NLB, LVS/IPVS, HAProxy tcp, Nginx stream | AWS ALB, Nginx http, HAProxy http, Envoy, Traefik |
| 잘 맞는 곳 | 대량 연결, 비 HTTP 서비스, 고정 IP가 필요할 때 | 마이크로서비스 라우팅, 웹·API, 카나리 배포 |

L3

패킷만

L4

연결

L7

요청·내용

▲ 계층별로 "얼마나 많은 정보를 보고 판단하는가"를 상대적으로 나타낸 그림입니다 (실측 수치가 아닙니다).

📌 gRPC를 L4로 나누면 생기는 일

gRPC는 HTTP/2 연결 하나에 많은 요청을 계속 실어 보냅니다. L4 로드밸런서는 연결 단위로만 나누므로, 연결이 몇 개 안 되면 특정 서버 한두 대에 요청이 몰립니다. gRPC는 L7(요청 단위) 로드밸런서나 클라이언트 측 로드밸런싱을 쓰는 것이 일반적입니다.

## 08 부하 분산 알고리즘

**한 줄 답:** 계층이 "무엇을 보고 나누느냐"라면, 알고리즘은 "어떤 규칙으로 서버를 고르느냐"입니다. 상황에 맞는 알고리즘을 골라야 서버가 고르게 일합니다.

| 알고리즘 | 방법 | 잘 맞는 상황 | 주의할 점 |
|----|----|----|----|
| 라운드 로빈 | 서버 1 → 2 → 3 → 1 순서로 돌아가며 보냅니다. | 서버 성능이 같고 요청 처리 시간이 비슷할 때 | 오래 걸리는 요청이 한 서버에 몰릴 수 있습니다. |
| 가중 라운드 로빈 | 서버마다 가중치를 주고 그 비율만큼 보냅니다. | 서버 사양이 다를 때, 카나리 배포 | 가중치를 직접 관리해야 합니다. |
| 최소 연결 (Least Connections) | 현재 연결이 가장 적은 서버로 보냅니다. | 연결 시간이 제각각일 때 (DB, WebSocket) | 연결 수 추적 비용이 조금 듭니다. |
| 최소 응답 시간 | 응답이 가장 빠른 서버로 보냅니다. | 서버 상태가 자주 변할 때 | 일부 상용·오픈소스 제품에서만 지원합니다 (예: Nginx Plus의 least_time). |
| IP 해시 | 클라이언트 IP를 해시해 항상 같은 서버로 보냅니다. | 쿠키 없이 세션 유지가 필요할 때 | 회사 NAT처럼 많은 사용자가 같은 IP면 한 서버에 몰립니다. |
| 일관된 해시 (Consistent Hashing) | 서버를 해시 링에 올려, 서버가 늘거나 줄어도 일부 키만 다른 서버로 옮겨 갑니다. | 캐시 서버, 샤딩 | 가상 노드 수를 충분히 둬야 고르게 퍼집니다. |
| 무작위 2개 중 선택 (Power of Two Choices) | 무작위로 두 서버를 골라 그중 덜 바쁜 쪽으로 보냅니다. | 대규모 분산 환경 (Envoy, HAProxy 지원) | \- |

▶ Nginx에서 알고리즘 바꾸기

```
upstream app {
    # 아무것도 안 쓰면 라운드 로빈
    # least_conn;                         # 최소 연결
    # ip_hash;                            # 클라이언트 IP 해시
    hash $request_uri consistent;         # URL 기준 일관된 해시 (캐시 서버 앞에 좋음)

    server 10.0.5.11:8080;
    server 10.0.5.12:8080;
    server 10.0.5.13:8080 backup;         # 나머지가 모두 죽었을 때만 사용
}
```

## 09 헬스 체크와 세션 유지

**한 줄 답:** 헬스 체크는 죽은 서버로 요청이 가지 않게 하는 기능이고, 세션 유지(sticky session)는 같은 사용자를 같은 서버로 보내는 기능입니다. 둘 다 로드밸런서를 실제로 운영할 때 꼭 정해야 합니다.

### 헬스 체크도 계층이 있습니다

| 종류 | 확인 방법 | 알 수 있는 것 |
|----|----|----|
| L3 체크 | ICMP ping | 서버가 네트워크에 살아 있는지 |
| L4 체크 | TCP 포트 연결 시도 | 프로세스가 포트를 듣고 있는지 |
| L7 체크 | `GET /health` 요청 후 200 응답 확인 | 애플리케이션이 실제로 정상 처리하는지 (DB 연결 등 포함 가능) |

포트는 열려 있는데 애플리케이션이 멈춘 경우는 L4 체크로는 잡히지 않습니다. 웹 서비스라면 가능하면 L7 헬스 체크를 쓰는 것이 좋습니다. 또 헬스 체크는 **능동** (로드밸런서가 주기적으로 찔러 봄)과 **수동** (실제 요청이 연속 실패하면 제외, Nginx의 `max_fails`) 두 가지가 있습니다.

### 세션 유지와 그 대안

로그인 정보를 서버 메모리에 저장하는 서비스는, 다음 요청이 다른 서버로 가면 로그인이 풀립니다. 이를 막는 방법은 세 가지입니다.

| 방법 | 설명 | 평가 |
|----|----|----|
| 스티키 세션 | L7은 쿠키(예: ALB의 `AWSALB` 쿠키), L4는 IP 해시로 같은 서버에 고정합니다. | 쉽지만 서버가 죽으면 그 사용자 세션이 사라지고, 부하가 고르지 않을 수 있습니다. |
| 세션 저장소 분리 | 세션을 Redis 같은 외부 저장소에 둡니다 (Spring Session 등). | 어느 서버로 가도 같은 세션을 읽을 수 있어 가장 많이 쓰는 방식입니다. |
| 토큰 방식 | JWT처럼 클라이언트가 인증 정보를 들고 다니게 합니다. | 서버가 상태를 갖지 않아(stateless) 확장에 유리합니다. 토큰 폐기 전략이 필요합니다. |

## 10 DNS 로드밸런싱과 GSLB

**한 줄 답:** DNS 로드밸런싱은 같은 도메인 조회에 서로 다른 IP를 돌려줘서 트래픽을 나누는 방식이고, 이를 지역·데이터센터 단위로 확장하고 헬스 체크까지 붙인 것이 **GSLB** (Global Server Load Balancing)입니다. DNS는 7계층 프로토콜이므로 넓게 보면 7계층 분산에 속합니다.

| 정책 | 설명 |
|----|----|
| 지역 기반 | 한국 사용자에게는 서울 리전 IP, 미국 사용자에게는 미국 리전 IP를 돌려줍니다. |
| 지연 시간 기반 | 사용자와 네트워크 지연이 가장 짧은 리전을 고릅니다. |
| 장애 조치 (Failover) | 주 데이터센터가 헬스 체크에 실패하면 보조 데이터센터 IP를 돌려줍니다. |
| 가중치 기반 | 정해진 비율로 여러 IP를 나눠 줍니다. |

⚠ DNS 방식의 한계

클라이언트와 중간 DNS 서버가 응답을 TTL 동안 캐시하므로, 서버를 빼도 즉시 반영되지 않습니다. 그래서 GSLB는 "어느 지역으로 보낼지"를 정하고, 각 지역 안에서는 L4·L7 로드밸런서가 실제 서버를 고르는 식으로 함께 씁니다.

▶ DNS가 여러 IP를 돌려주는지 확인

```
# A 레코드가 여러 개면 DNS 수준에서 분산하고 있다는 뜻
dig +short A www.google.com
dig +short A www.naver.com
```

## 11 클라우드 로드밸런서 고르기

**한 줄 답:** 주요 클라우드는 L4와 L7 로드밸런서를 따로 제공합니다. HTTP 서비스면 L7, 비 HTTP나 고정 IP·초고성능이 필요하면 L4를 고르는 것이 기본입니다.

| 클라우드 | L7 | L4 | L3 · 기타 |
|----|----|----|----|
| AWS | Application Load Balancer (ALB) | Network Load Balancer (NLB) | Gateway Load Balancer (GWLB), Route 53(DNS) |
| Google Cloud | Application Load Balancer | Network Load Balancer (프록시형 / 패스스루형) | Cloud DNS |
| Azure | Application Gateway, Front Door | Azure Load Balancer | Gateway Load Balancer, Traffic Manager(DNS) |
| 쿠버네티스 | Ingress, Gateway API (HTTPRoute) | Service type LoadBalancer | kube-proxy(iptables/IPVS)가 노드 안에서 L4 분산 |

### 고르는 순서

Q1 · HTTP인가?

HTTP·HTTPS·gRPC 요청을 경로나 호스트별로 나눠야 하면 → **L7**

Q2 · HTTP가 아닌가?

DB, Redis, MQTT, 게임 UDP처럼 HTTP가 아니면 → **L4**

Q3 · 고정 IP·초저지연?

고정 IP가 필요하거나 초당 수백만 연결 수준이면 → **L4 (NLB 등)**

Q4 · 여러 지역?

리전 단위 장애 대비가 필요하면 → **GSLB(DNS)** + 각 리전 L4/L7

## 12 직접 해보기: Docker로 L7 로드밸런서 만들기

**한 줄 답:** Nginx 한 대와 작은 웹 서버 두 대로 라운드 로빈 분산을 5분 안에 눈으로 확인할 수 있습니다.

▶ 1단계 · docker-compose.yml

```
services:
  web1:
    image: hashicorp/http-echo
    command: ["-text=hello from web1"]
  web2:
    image: hashicorp/http-echo
    command: ["-text=hello from web2"]
  lb:
    image: nginx:stable
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on: [web1, web2]
```

▶ 2단계 · nginx.conf (L7 라운드 로빈)

```
upstream echo {
    server web1:5678;
    server web2:5678;
}
server {
    listen 80;
    location / {
        proxy_pass http://echo;
        add_header X-Upstream $upstream_addr;   # 어느 서버로 갔는지 응답 헤더에 표시
    }
}
```

▶ 3단계 · 실행하고 분산 확인

```
docker compose up -d

# 6번 요청 → web1, web2가 번갈아 응답
for i in $(seq 1 6); do curl -s localhost:8080; done

# 한 대를 멈추면 Nginx가 실패를 감지하고 남은 서버로만 보냄 (수동 헬스 체크)
docker compose stop web2
for i in $(seq 1 4); do curl -s localhost:8080; done

docker compose down
```

여기서 `upstream` 블록에 `least_conn;`이나 `ip_hash;`를 넣어 알고리즘을 바꿔 보고, 같은 구성을 `stream` 블록으로 바꿔 L4로 돌려 보면 두 방식의 차이를 직접 느낄 수 있습니다.

## 정리

**핵심 1.** 로드밸런서의 종류는 OSI 몇 계층 정보까지 보고 판단하느냐로 나뉩니다. L2는 MAC, L3는 IP, L4는 IP와 포트, L7은 URL·헤더·쿠키까지 봅니다.

**핵심 2.** L4는 연결 단위로 빠르게 나누고 어떤 TCP·UDP 프로토콜이든 처리합니다. L7은 요청 단위로 경로·호스트별 라우팅, TLS 종료, 쿠키 기반 세션 유지 같은 세밀한 기능을 제공합니다.

**핵심 3.** 계층과 함께 분산 알고리즘, L7 헬스 체크, 세션 저장 방식을 정해야 합니다. 큰 서비스는 GSLB → L3/L4 → L7 → 서버처럼 여러 계층을 쌓아서 씁니다.

✦ 지금 해볼 것

☐ 지금 운영 중인 서비스의 로드밸런서가 L4인지 L7인지, 헬스 체크가 몇 계층인지 확인하기

☐ 서버 로그에 찍히는 클라이언트 IP가 실제 사용자 IP인지(`X-Forwarded-For` 설정) 확인하기

☐ 위 Docker 예제로 라운드 로빈과 `least_conn`, `ip_hash`를 바꿔 가며 결과 비교하기

## 자주 묻는 질문

### L4 로드밸런서와 L7 로드밸런서의 차이는 무엇인가요?

L4 로드밸런서는 OSI 4계층 정보인 IP 주소와 포트 번호만 보고 TCP 연결 단위로 서버를 고르므로 빠르고, HTTP가 아닌 프로토콜도 처리합니다. L7 로드밸런서는 7계층인 HTTP를 해석해 URL 경로, 호스트, 헤더, 쿠키를 보고 요청 단위로 서버를 고르며, TLS 종료와 경로별 라우팅을 할 수 있습니다. AWS 기준으로 NLB가 L4, ALB가 L7입니다.

### L2, L3 로드밸런서도 있나요?

있습니다. L2 방식은 프레임의 도착 MAC 주소만 실제 서버 것으로 바꾸는 DSR(Direct Server Return)이 대표적이며, 응답이 로드밸런서를 거치지 않아 부담이 적습니다. L3 방식은 라우터의 ECMP나 Anycast처럼 IP와 경로만으로 트래픽을 나누며, AWS Gateway Load Balancer도 3계층에서 동작합니다.

### 로드밸런서를 쓰면 로그인 세션이 풀리는 이유는 무엇인가요?

세션을 서버 메모리에 저장하면, 다음 요청이 다른 서버로 갔을 때 그 서버에는 세션 정보가 없기 때문입니다. 쿠키나 IP 해시로 같은 서버에 고정하는 스티키 세션을 쓰거나, Redis 같은 외부 세션 저장소 또는 JWT 같은 토큰 방식을 쓰면 해결됩니다. 확장성과 장애 대비를 생각하면 외부 세션 저장소가 가장 널리 쓰입니다.

## 참고 자료

[AWS · How Elastic Load Balancing works ↗](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html) [AWS · ELB 제품 비교 (ALB, NLB, GWLB) ↗](https://aws.amazon.com/elasticloadbalancing/features/) [Google Cloud · Load balancing overview ↗](https://cloud.google.com/load-balancing/docs/load-balancing-overview) [Azure · Load balancing options ↗](https://learn.microsoft.com/azure/architecture/guide/technology-choices/load-balancing-overview) [Nginx · HTTP load balancing ↗](https://nginx.org/en/docs/http/load_balancing.html) [Nginx · stream upstream 모듈 ↗](https://nginx.org/en/docs/stream/ngx_stream_upstream_module.html) [HAProxy 문서 ↗](https://docs.haproxy.org/) [LVS · Virtual Server via Direct Routing ↗](https://www.linuxvirtualserver.org/VS-DRouting.html) [RFC 2992 · Multipath (ECMP) 분석 ↗](https://www.rfc-editor.org/rfc/rfc2992)

---

`#로드밸런서` `#LoadBalancer` `#L4로드밸런서` `#L7로드밸런서` `#OSI7계층` `#부하분산` `#Nginx` `#HAProxy` `#AWSALB` `#ComputerScience`
