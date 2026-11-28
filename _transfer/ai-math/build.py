#!/usr/bin/env python3
"""간단한 마크업(src/*.src.html) → 티스토리용 인라인 스타일 HTML. post-components.html 스타일 그대로."""
import html, re, sys, time
from pathlib import Path

P = 'margin: 0 0 16px; line-height: 1.85;'
H2 = 'margin: 48px 0 18px; font-size: 24px; line-height: 1.4; font-weight: 800; padding-bottom: 12px; border-bottom: 3px solid #d6e0fb;'
H3 = 'margin: 26px 0 8px; font-size: 19px; font-weight: 700;'
TH = 'text-align: left; background: #eef3ff; color: #163c9e; padding: 12px 16px; border-top: 2px solid #2357d9;'
TD = 'padding: 12px 16px; border-bottom: 1px solid #e3e6eb; vertical-align: top;'
CODE = 'background: #eef1f5; color: #c7254e; padding: 2px 6px; border-radius: 4px; font-size: 14px;'
NUM = 'display: inline-block; width: 22px; height: 22px; line-height: 22px; text-align: center; border-radius: 6px; background: #2357d9; color: #ffffff; font-size: 12px; font-weight: bold; margin-right: 10px;'
_ts = [int(time.time() * 1000)]
import json as _json
_U = Path(__file__).resolve().parent / 'urls.json'
EXTRA_URLS = _json.loads(_U.read_text()) if _U.exists() else {}
IMGDIR = Path(__file__).resolve().parent.parent / 'images'


def li_items(s):
    return re.findall(r"<li>(.*?)</li>", s, re.S)


def build(src: str) -> str:
    # 맨 위 메타 주석만 (코드 블록 안의 예시 주석은 건드리지 않음)
    head = re.match(r"(\s*<!--\s*(?:제목|태그|커버|슬러그):.*?-->)+", src)
    meta = re.findall(r"<!--.*?-->", head.group(0)) if head else []
    body = src[head.end():] if head else src

    # 코드 블록 (먼저 빼 두기: 안쪽은 이스케이프만)
    blocks = []
    def code_block(m):
        lang, label, code = m.group(1), m.group(2), m.group(3).strip("\n")
        _ts[0] += 1
        out = ''
        if label:
            out += f'<p style="margin: 20px 0 6px; font-size: 14px; color: #5b6474;">▶ {html.escape(label, quote=False)}</p>\n'
        out += f'<pre id="code_{_ts[0]}" class="{lang}" data-ke-language="{lang}" data-ke-type="codeblock"><code>{html.escape(code, quote=False)}</code></pre>'
        blocks.append(out)
        return f"@@BLOCK{len(blocks)-1}@@"
    body = re.sub(r'<cb lang="(\w+)"(?: label="(.*?)")?>(.*?)</cb>', code_block, body, flags=re.S)
    body = re.sub(r"<!--.*?-->\s*", "", body, flags=re.S)

    # 목차
    heads = re.findall(r'<h2 n="(\d+)" id="(\w+)">(.*?)</h2>', body)
    toc = '<div style="border: 1px solid #e3e6eb; border-radius: 14px; padding: 16px 22px; margin: 0 0 32px;">\n<p style="margin: 0 0 6px; font-size: 14px; color: #5b6474; font-weight: bold;">목차</p>\n'
    toc += "\n".join(f'<p style="margin: 0 0 2px;"><a href="#{i}" style="color: #2357d9; text-decoration: none;">{int(n)}. {re.sub("<.*?>", "", t)}</a></p>' for n, i, t in heads)
    toc += '\n</div>'
    body = body.replace("<toc/>", toc)

    body = re.sub(r'<h2 n="(\d+)" id="(\w+)">(.*?)</h2>',
                  lambda m: f'<h2 id="{m.group(2)}" style="{H2}"><span style="color: #2357d9; margin-right: 10px;">{m.group(1)}</span>{m.group(3)}</h2>', body)
    body = re.sub(r'<h2 id="(\w+)">', lambda m: f'<h2 id="{m.group(1)}" style="{H2}">', body)
    body = body.replace("<h3>", f'<h3 style="{H3}">')

    def tldr(m):
        items = li_items(m.group(1))
        rows = "\n".join(f'<p style="margin: 0 0 {0 if k == len(items)-1 else 8}px; color: #eef2fb;"><span style="{NUM}">{k+1}</span>{t}</p>' for k, t in enumerate(items))
        return f'<div style="background: #0f1b33; color: #eef2fb; border-radius: 16px; padding: 24px 28px; margin: 0 0 24px;">\n<p style="margin: 0 0 12px; font-size: 12px; letter-spacing: 1.5px; color: #8fb0ff; font-weight: bold;">TL;DR · 한눈에 보기</p>\n{rows}\n</div>'
    body = re.sub(r"<tldr>(.*?)</tldr>", tldr, body, flags=re.S)

    body = re.sub(r'<why(?: t="(.*?)")?>(.*?)</why>', lambda m:
        f'<div style="background: #fff8e6; border: 1px solid #f3dfa6; border-radius: 14px; padding: 18px 22px; margin: 24px 0;">\n<p style="margin: 0 0 4px; font-weight: bold; color: #7a4d00;">{m.group(1) or "💡 왜 중요할까"}</p>\n<p style="margin: 0; color: #3b3220; line-height: 1.8;">{m.group(2).strip()}</p>\n</div>', body, flags=re.S)
    body = re.sub(r'<note(?: t="(.*?)")?>(.*?)</note>', lambda m:
        f'<div style="background: #eef3ff; border: 1px solid #d6e0fb; border-radius: 14px; padding: 18px 22px; margin: 24px 0;">\n<p style="margin: 0 0 4px; font-weight: bold; color: #163c9e;">{m.group(1) or "📌 알아둘 점"}</p>\n<p style="margin: 0; color: #1b2a4a; line-height: 1.8;">{m.group(2).strip()}</p>\n</div>', body, flags=re.S)

    def steps(m):
        cards = re.findall(r'<s t="(.*?)">(.*?)</s>', m.group(1), re.S)
        inner = "\n".join(f'<div style="flex: 1 1 180px; background: #f4f6fa; border-radius: 12px; padding: 16px 18px;"><p style="margin: 0; font-size: 12px; color: #2357d9; font-weight: bold;">{t}</p><p style="margin: 4px 0 0; font-size: 15px; color: #1b1f27; line-height: 1.6;">{x.strip()}</p></div>' for t, x in cards)
        return f'<div style="display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 20px;">\n{inner}\n</div>'
    body = re.sub(r"<steps>(.*?)</steps>", steps, body, flags=re.S)

    def check(m):
        items = li_items(m.group(1))
        rows = "\n".join(f'<p style="margin: 0 0 {0 if k == len(items)-1 else 4}px;">☐ {t}</p>' for k, t in enumerate(items))
        return f'<div style="border: 2px solid #1b1f27; padding: 18px 22px; margin: 0 0 24px; box-shadow: 4px 4px 0 #1b1f27;">\n<p style="margin: 0 0 8px; font-weight: bold; color: #e8890c;">✦ 지금 해볼 것</p>\n{rows}\n</div>'
    body = re.sub(r"<check>(.*?)</check>", check, body, flags=re.S)

    body = re.sub(r'<src href="(.*?)">(.*?)</src>', lambda m:
        f'<a href="{m.group(1)}" style="display: inline-block; font-size: 13px; color: #5b6474; border: 1px solid #e3e6eb; border-radius: 999px; padding: 5px 14px; margin: 0 6px 6px 0; text-decoration: none;">{m.group(2)} ↗</a>', body)
    body = body.replace("<srcs>", '<p style="margin: 8px 0 0;">').replace("</srcs>", "</p>")
    body = re.sub(r"<quote>(.*?)</quote>", r'<blockquote style="margin: 28px 0; padding: 4px 0 4px 20px; border-left: 4px solid #2357d9; font-size: 18px; font-weight: bold; line-height: 1.6;">\1</blockquote>', body, flags=re.S)


    # 막대 차트
    def chart(m):
        bars = re.findall(r'<bar v="(\d+)" max="(\d+)" t="(.*?)">(.*?)</bar>', m.group(1))
        rows = "\n".join(f'<div style="display: flex; align-items: center; gap: 10px; margin: 0 0 8px;"><span style="width: 44px; font-size: 13px; color: #5b6474; font-weight: bold;">{t}</span><div style="flex: 1; background: #eef1f5; border-radius: 6px; height: 22px;"><div style="width: {int(v)*100//int(mx)}%; background: #2357d9; height: 22px; border-radius: 6px;"></div></div><span style="width: 56px; font-size: 13px; text-align: right;">{lab}</span></div>' for v, mx, t, lab in bars)
        return f'<div style="border: 1px solid #e3e6eb; border-radius: 14px; padding: 18px 22px; margin: 20px 0;">\n{rows}\n</div>'
    body = re.sub(r"<chart>(.*?)</chart>", chart, body, flags=re.S)
    # 캡처 자리: images/<n>.png 가 있으면 표시 자리(@@IMGn@@), 없으면 제거
    def slot(m):
        n, cap = m.group(1), m.group(2)
        if not (IMGDIR / f"{n}.png").exists():
            return ""
        c = f'\n<p style="margin: -6px 0 24px; font-size: 13px; color: #8b95a1; text-align: center;">{cap}</p>\n' if cap else "\n"
        return f"<p>@@IMG{n}@@</p>{c}"
    body = re.sub(r'<slot n="(\d+)"(?: cap="(.*?)")?/>\s*', slot, body)

    SERIES = [("1탄", "리만 가설", "167년 난제에 AI가 두 번 도전한 이야기"),
              ("2탄", "양자 알고리즘", "AI가 양자 회로를 설계하고 증명까지"),
              ("3탄", "VP ≠ VNP", "Claude와 OpenAI, 몇 시간 차이의 증명 공개"),
              ("4탄", "OpenAI 9편", "하루에 올라온 수학 논문 아홉 편"),
              ("5탄", "구글 6편", "Cogentic과 소인수분해 난제")]
    def series(m):
        cur = m.group(1); rows = []
        URLS = dict(EXTRA_URLS)
        for no, st, desc in SERIES:
            on = no == cur
            bg = "#eef3ff" if on else "#ffffff"
            badge = '<span style="display: inline-block; margin-left: 8px; font-size: 11px; color: #ffffff; background: #2357d9; border-radius: 999px; padding: 1px 8px; vertical-align: middle;">지금 읽는 글</span>' if on else ('' if no in URLS else '<span style="display: inline-block; margin-left: 8px; font-size: 11px; color: #5b6474; border: 1px solid #d5dae1; border-radius: 999px; padding: 0 8px; vertical-align: middle;">예정</span>')
            txt = (f'<a href="{URLS[no]}" style="color: #1b1f27; text-decoration: underline; text-decoration-color: #9db4f0;">{desc}</a>' if no in URLS and not on else desc)
            if on: txt = f"<b>{txt}</b>"
            rows.append(f'<div style="display: flex; gap: 14px; align-items: flex-start; padding: 12px 16px; background: {bg}; border-top: 1px solid #e3e6eb;"><span style="flex: 0 0 130px; white-space: nowrap; font-weight: bold; color: #2357d9;">{no} · {st}</span><span style="flex: 1; color: #1b1f27; line-height: 1.6;">{txt}{badge}</span></div>')
        return '<div style="border: 1px solid #e3e6eb; border-radius: 14px; overflow: hidden; margin: 0 0 28px;">\n<p style="margin: 0; padding: 12px 16px; font-size: 14px; font-weight: bold; color: #163c9e; background: #f7f9fc;">📚 AI가 뒤집어놓은 수학계 시리즈</p>\n' + "\n".join(rows) + "\n</div>"
    body = re.sub(r'<series cur="(.*?)"/>', series, body)

    # 표
    body = body.replace("<table>", '<div style="overflow-x: auto; margin: 20px 0;">\n<table style="width: 100%; border-collapse: collapse; font-size: 15px; line-height: 1.6;">').replace("</table>", "</table>\n</div>")
    body = body.replace("<th>", f'<th style="{TH}">').replace("<td>", f'<td style="{TD}">').replace("<td b>", f'<td style="{TD} font-weight: bold; white-space: nowrap;">')
    body = body.replace("<code>", f'<code style="{CODE}">')
    body = body.replace("<p>", f'<p style="{P}">')
    body = body.replace("<hr/>", '<hr style="border: none; border-top: 1px solid #e3e6eb; margin: 40px 0;">')

    for k, b in enumerate(blocks):
        body = body.replace(f"@@BLOCK{k}@@", b)
    return "\n".join(meta) + "\n" + body.strip() + "\n"


if __name__ == "__main__":
    for f in sys.argv[1:]:
        src = Path(f).resolve()
        out = src.parent.parent / src.name.replace(".src.html", ".html")
        out.write_text(build(src.read_text(encoding="utf-8")), encoding="utf-8")
        text = re.sub(r"<[^>]+>", "", re.sub(r"<pre.*?</pre>", "", out.read_text(encoding="utf-8"), flags=re.S))
        print(out, f"{out.stat().st_size//1024}KB, 본문 글자 약 {len(re.sub(r'\s+', ' ', text))}자")
