#!/usr/bin/env python3
"""발행 직후 깃허브 보관. published.json + 초안 + 커버로 scripts/add_post.py를 돌리고 push.

python3.12 archive.py --date 2026-11-26 [--no-push]
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
from config import ARCHIVE_REPO, BOT_PY, CATS, day_dir, notify, read_meta, strip_meta


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
        raw = (d / "drafts" / f"{key}.html").read_text(encoding="utf-8")
        meta = read_meta(raw)
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(strip_meta(raw))
        cmd = [BOT_PY, str(ARCHIVE_REPO / "scripts/add_post.py"), "--category", CATS[key]["slug"], "--date", a.date,
               "--slug", slugify(meta, info["title"]), "--title", info["title"], "--url", info["url"],
               "--tags", ",".join(info["tags"]), "--html", tmp.name]
        cover = d / "covers" / f"{key}-cover.png"
        if cover.exists():
            cmd += ["--cover", str(cover)]
        subprocess.run(cmd, check=True); added += 1
    if not added:
        print("보관할 공개 글이 없어요"); return
    git("add", "-A")
    git("commit", "-m", f"📝 {a.date} 오늘의 IT {added}편")
    if not a.no_push:
        try:
            git("push", "origin", "main")
        except subprocess.CalledProcessError as e:
            notify("daily-bytes 깃허브 push 실패", e.stderr[:200]); sys.exit(1)
    print(f"{added}편 보관 완료")


if __name__ == "__main__":
    main()
