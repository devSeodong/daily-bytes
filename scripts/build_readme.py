#!/usr/bin/env python3
"""모든 글의 front matter를 읽어 README.md를 다시 만든다."""
import re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from categories import CATEGORIES  # noqa: E402

BLOG = "https://dongseodong.tistory.com/"
RECENT_DAYS = 7


def read_meta(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta


def posts():
    out = []
    for cat in CATEGORIES:
        for p in sorted((ROOT / cat).glob("*/*/*.md")):
            meta = read_meta(p)
            if meta:
                meta["cat"] = cat
                meta["path"] = p.relative_to(ROOT).as_posix()
                out.append(meta)
    out.sort(key=lambda x: list(CATEGORIES).index(x["cat"]))
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


def short(title: str) -> str:
    # "오늘의 AI 이슈 (2026.11.24) - 부제" → "부제"
    return title.split(" - ", 1)[1] if " - " in title else title


def main():
    all_posts = posts()
    by_date = defaultdict(list)
    for p in all_posts:
        by_date[p["date"]].append(p)
    dates = sorted(by_date, reverse=True)

    L = []
    L.append("# 📚 daily-bytes\n")
    L.append("> 매일 한 입(byte)씩 쌓이는 IT 기록. [서동이의 코딩일기]({}) **오늘의 IT** 시리즈 아카이브예요.\n".format(BLOG))
    L.append(f"![posts](https://img.shields.io/badge/posts-{len(all_posts)}-7C5CFF) "
             f"![days](https://img.shields.io/badge/days-{len(dates)}-10B981) "
             f"![updated](https://img.shields.io/badge/updated-{dates[0].replace('-', '--') if dates else 'none'}-F59E0B)\n")
    L.append("매일 저녁 8시(KST), 티스토리에 세 편이 올라오면 이곳에도 마크다운으로 함께 쌓여요.\n")
    L.append("| 카테고리 | 내용 | 글 수 |\n|---|---|---|")
    for key, c in CATEGORIES.items():
        n = sum(1 for p in all_posts if p["cat"] == key)
        L.append(f"| {c['emoji']} [{c['label']}](./{key}) | {c['desc']} | {n} |")
    L.append("")

    L.append(f"## 🗓️ 최근 {RECENT_DAYS}일\n")
    for d in dates[:RECENT_DAYS]:
        L.append(f"### {d}\n")
        for p in by_date[d]:
            c = CATEGORIES[p["cat"]]
            L.append(f"- {c['emoji']} **{c['label']}** · [{short(p['title'])}]({p['path']}) · [티스토리]({p['tistory']})")
        L.append("")

    older = dates[RECENT_DAYS:]
    if older:
        L.append("## 🗄️ 지난 글\n")
        for d in older:
            items = " · ".join(f"[{CATEGORIES[p['cat']]['emoji']} {short(p['title'])}]({p['path']})" for p in by_date[d])
            L.append(f"- **{d}** · {items}")
        L.append("")

    L.append("## 📁 구조\n")
    L.append("```\n<카테고리>/<연>/<월>/<날짜>-<slug>.md\n<카테고리>/<연>/<월>/assets/   # 대표 이미지\n```\n")
    L.append(f"📝 매일 새 글은 [티스토리]({BLOG})에서 먼저 만나보세요!")
    L.insert(0, "<!-- 이 README는 scripts/build_readme.py가 자동으로 만듭니다. 직접 고치지 말고 스크립트를 고쳐 주세요. -->")
    (ROOT / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # 카테고리별 README
    for key, c in CATEGORIES.items():
        items = [p for p in all_posts if p["cat"] == key]
        (ROOT / key).mkdir(exist_ok=True)
        lines = [f"# {c['emoji']} {c['label']}\n", f"> {c['desc']}\n"]
        month = None
        for p in items:
            ym = p["date"][:7]
            if ym != month:
                month = ym
                lines.append(f"\n## {ym}\n")
            rel = p["path"].split("/", 1)[1]
            lines.append(f"- {p['date']} · [{short(p['title'])}]({rel}) · [티스토리]({p['tistory']})")
        (ROOT / key / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
