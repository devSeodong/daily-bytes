#!/usr/bin/env python3
"""티스토리에 발행한 글(HTML)을 마크다운으로 바꿔 아카이브에 추가하고 README를 다시 만든다.

예시:
  python3 scripts/add_post.py \
    --category ai-issue --date 2026-11-24 --slug jensen-huang-returns \
    --title "오늘의 AI 이슈 (2026.11.24) - ..." \
    --url https://dongseodong.tistory.com/59 \
    --tags "AI뉴스,엔비디아,젠슨황" \
    --html path/to/post.html --cover path/to/cover.jpg

필요: python3, beautifulsoup4, pandoc
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from categories import CATEGORIES  # noqa: E402
import build_readme  # noqa: E402


def clean_html(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(["script", "style"]):
        t.decompose()
    for img in soup.find_all("img"):  # 본문 이미지는 티스토리 CDN이라 아카이브에선 빼고 커버만 둔다
        img.decompose()
    # 붙어 있는 인라인 조각(번호 배지 + 제목 등) 사이에 공백 넣기
    for t in soup.find_all(["span", "strong", "b"]):
        if t.next_sibling is not None and not str(t.next_sibling).startswith((" ", "\n")):
            t.insert_after(" ")
    for t in soup.find_all(True):
        for attr in ("style", "class", "id", "data-ke-style", "data-ke-size", "data-ke-type", "target", "rel"):
            t.attrs.pop(attr, None)
    return str(soup)


def to_markdown(html: str) -> str:
    out = subprocess.run(
        ["pandoc", "-f", "html-native_divs-native_spans", "-t", "gfm", "--wrap=none"],
        input=html, capture_output=True, text=True, check=True,
    ).stdout
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--category", required=True, choices=list(CATEGORIES))
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--slug", required=True, help="영문 소문자-하이픈")
    p.add_argument("--title", required=True)
    p.add_argument("--url", required=True, help="티스토리 글 주소")
    p.add_argument("--tags", default="", help="쉼표로 구분")
    p.add_argument("--html", required=True, help="본문 HTML 파일")
    p.add_argument("--cover", help="대표 이미지 파일 (jpg/png)")
    a = p.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date):
        sys.exit("--date 는 YYYY-MM-DD 형식이어야 해요")
    slug = re.sub(r"[^a-z0-9-]+", "-", a.slug.lower()).strip("-") or "post"
    y, m, _ = a.date.split("-")
    folder = ROOT / a.category / y / m
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{a.date}-{slug}"
    tags = [t.strip() for t in a.tags.split(",") if t.strip()]

    cover_line = ""
    cover_rel = ""
    if a.cover:
        assets = folder / "assets"
        assets.mkdir(exist_ok=True)
        ext = Path(a.cover).suffix.lower() or ".jpg"
        dest = assets / f"{name}{ext}"
        shutil.copyfile(a.cover, dest)
        cover_rel = f"assets/{dest.name}"
        cover_line = f"![대표 이미지]({cover_rel})\n\n"

    body = to_markdown(clean_html(Path(a.html).read_text(encoding="utf-8")))
    cat = CATEGORIES[a.category]
    front = [
        "---",
        f"title: {yaml_str(a.title)}",
        f"date: {a.date}",
        f"category: {yaml_str(cat['label'])}",
        f"tistory: {a.url}",
        "tags: [" + ", ".join(yaml_str(t) for t in tags) + "]",
    ]
    if cover_rel:
        front.append(f"cover: {cover_rel}")
    front.append("---\n")

    md = "\n".join(front)
    md += f"# {a.title}\n\n"
    md += f"> {cat['emoji']} **{cat['label']}** · {a.date} · 📝 [티스토리에서 보기]({a.url})\n\n"
    md += cover_line
    md += body
    if tags:
        md += "\n---\n\n" + " ".join(f"`#{t}`" for t in tags) + "\n"

    path = folder / f"{name}.md"
    path.write_text(md, encoding="utf-8")
    print(path.relative_to(ROOT))
    build_readme.main()


if __name__ == "__main__":
    main()
