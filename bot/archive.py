#!/usr/bin/env python3
"""발행 직후 깃허브 보관. published.json + 초안 + 커버로 scripts/add_post.py를 돌리고 push.

python3.12 archive.py --date 2026-11-26 [--no-push]
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
from config import ARCHIVE_REPO, BOT_PY, cat, day_dir, notify, read_meta, strip_meta


def git(*args):
    return subprocess.run(["git", "-C", str(ARCHIVE_REPO), *args], check=True, capture_output=True, text=True).stdout


def slugify(meta, title):
    if meta.get("슬러그"):
        return meta["슬러그"]
    s = re.sub(r"[^A-Za-z0-9]+", "-", title.split(" - ", 1)[-1]).strip("-").lower()
    return "-".join(s.split("-")[:6]) or "post"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True); ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    d = day_dir(a.date)
    pub = json.loads((d / "published.json").read_text())
    git("checkout", "main"); git("pull", "--ff-only")
    added = 0
    for key, info in pub.items():
        if info.get("visibility") != "public" or not info.get("url"):
            continue  # 테스트(비공개) 글은 보관 안 함
        y, m = a.date[:4], a.date[5:7]
        raw = (d / "drafts" / f"{key}.html").read_text(encoding="utf-8")
        meta = read_meta(raw)
        slug = slugify(meta, info["title"])
        # 심층 시리즈는 하루에 여러 편이라 슬러그까지 맞춰 봄. 정규 글은 하루 한 편이라 날짜만.
        pat = f"{a.date}-{slug}.md" if key.startswith("ai-deep-") else f"{a.date}-*.md"
        done = list((ARCHIVE_REPO / cat(key)["slug"] / y / m).glob(pat))
        if done:
            print(f"{key}: 이미 보관됨 ({done[0].name}), 건너뜀"); continue
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(strip_meta(raw))
        cmd = [BOT_PY, str(ARCHIVE_REPO / "scripts/add_post.py"), "--category", cat(key)["slug"], "--date", a.date,
               "--slug", slug, "--title", info["title"], "--url", info["url"],
               "--tags", ",".join(info["tags"]), "--html", tmp.name]
        cover = d / "covers" / f"{key}-cover.png"
        if cover.exists():
            cmd += ["--cover", str(cover)]
        subprocess.run(cmd, check=True); added += 1
    if added:
        git("add", "-A")
        if git("status", "--porcelain").strip():
            labels = [cat(k)["label"] for k, i in pub.items() if i.get("visibility") == "public" and i.get("url")]
            msg = f"📝 {a.date} 오늘의 IT: {labels[0]}" if added == 1 and labels else f"📝 {a.date} 오늘의 IT {added}편"
            git("commit", "-m", msg)
    ahead = int(git("rev-list", "--count", "origin/main..main").strip() or 0)
    if not ahead:
        print("새로 보관할 공개 글이 없어요"); return
    if not a.no_push:
        try:
            git("push", "origin", "main")
        except subprocess.CalledProcessError as e:
            notify("daily-bytes 깃허브 push 실패", e.stderr[:200]); sys.exit(1)
    print(f"{added}편 보관 완료 (push 대기 커밋 {ahead}개)")


if __name__ == "__main__":
    main()
