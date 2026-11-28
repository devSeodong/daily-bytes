#!/usr/bin/env python3
"""이미 발행한 AI 심층 분석 글의 제목·본문·대표 이미지를 새 초안으로 바꿔 수정 발행한다.

사용: cd ~/daily-bytes-src/bot && ~/daily-bytes-bot/venv/bin/python ~/Desktop/취준/_blog-drafts/ai-math/edit_posts.py 2026-11-28 ai-deep-01-riemann ai-deep-02-quantum ai-deep-03-vpvnp
- 초안: ~/daily-bytes-bot/work/<date>/drafts/<key>.html (제목은 <!-- 제목: --> 주석)
- 대표 이미지: ~/daily-bytes-bot/work/<date>/covers/<key>-cover.png (thumb.py 로 먼저 다시 만들 것)
- 글 주소: published.json 의 url. 태그·카테고리·공개 범위는 그대로 둔다.
"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from config import BLOG, day_dir, read_meta, strip_meta  # noqa: E402
from publish import browser, logged_in, save_state, set_body, VIS  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def main():
    date, keys = sys.argv[1], sys.argv[2:]
    d = day_dir(date)
    out = d / "published.json"
    pub = json.loads(out.read_text())
    with sync_playwright() as p:
        ctx, page = browser(p)
        if not logged_in(page):
            ctx.close(); sys.exit("로그인 만료")
        for key in keys:
            raw = (d / "drafts" / f"{key}.html").read_text(encoding="utf-8")
            title = read_meta(raw)["제목"]
            cover = d / "covers" / f"{key}-cover.png"
            pid = pub[key]["url"].rstrip("/").split("/")[-1]
            page.goto(f"{BLOG}/manage/newpost/{pid}?type=post", wait_until="domcontentloaded")
            page.wait_for_selector("#post-title-inp", timeout=30000)
            page.fill("#post-title-inp", title)
            set_body(page, strip_meta(raw), cover if cover.exists() else None)
            page.click("#publish-layer-btn")
            page.wait_for_selector(VIS["public"], state="attached", timeout=10000)
            if not page.is_checked(VIS["public"]):
                page.click(f"label[for={VIS['public'][1:]}] .checkbox-text")
            if cover.exists():
                try:  # 기존 대표 이미지가 있으면 삭제 버튼부터
                    page.locator(".box_thumb .btn_del, .box_thumb button:has-text('삭제')").first.click(timeout=3000)
                except Exception:
                    pass
                page.set_input_files(".box_thumb input[type=file]", str(cover))
                time.sleep(3)
            with page.expect_navigation(timeout=60000):
                page.click("#publish-btn")
            time.sleep(2)
            pub[key]["title"] = title
            out.write_text(json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
            print(key, "수정 완료:", pub[key]["url"], title)
        save_state(ctx); ctx.close()


if __name__ == "__main__":
    main()
