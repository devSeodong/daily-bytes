#!/usr/bin/env python3
"""AI 심층 분석 시리즈: 발행된 글들의 시리즈 표에 서로 링크를 넣고 다시 저장(수정 발행)한다.

사용: ~/daily-bytes-bot/venv/bin/python deep_series.py 2026-11-28 [--dry]
- published.json 에서 ai-deep-* 키의 URL 을 읽어 urls.json 을 만들고
- 같은 폴더의 build.py 로 글마다 시리즈 표 HTML 을 새로 만든 뒤
- 티스토리 편집 화면에서 기존 시리즈 표(📚 ... 시리즈 문단의 부모 div)만 바꿔치기하고 다시 발행한다.
"""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path.home() / "daily-bytes-deep/bot"))
from config import BLOG, day_dir  # noqa: E402

NUM = {"01": "1탄", "02": "2탄", "03": "3탄", "04": "4탄", "05": "5탄"}


def main():
    date = sys.argv[1]; dry = "--dry" in sys.argv
    d = day_dir(date)
    pub = json.loads((d / "published.json").read_text())
    # 다른 날짜에 발행한 편도 포함하려고 ~/daily-bytes-bot/work/*/published.json 전체를 훑음
    urls = {}
    for f in (d.parent).glob("*/published.json"):
        for k, v in json.loads(f.read_text()).items():
            if k.startswith("ai-deep-") and v.get("url") and v.get("visibility") == "public":
                urls[NUM[k.split("-")[2]]] = v["url"]
    (HERE / "urls.json").write_text(json.dumps(urls, ensure_ascii=False, indent=2))
    import build  # urls.json 을 읽으며 import 됨
    print("시리즈 링크:", urls)
    todo = {k: v for k, v in pub.items() if k.startswith("ai-deep-") and v.get("url")}
    if dry:
        for k in todo:
            print(k, build.build(f'<series cur="{NUM[k.split("-")[2]]}"/>')[:200]); return
    from playwright.sync_api import sync_playwright
    from publish import browser, logged_in, save_state, VIS
    with sync_playwright() as p:
        ctx, page = browser(p)
        if not logged_in(page):
            ctx.close(); sys.exit("로그인 만료: publish.py --login 필요")
        for k, info in todo.items():
            html = build.build(f'<series cur="{NUM[k.split("-")[2]]}"/>').strip()
            pid = info["url"].rstrip("/").split("/")[-1]
            page.goto(f"{BLOG}/manage/newpost/{pid}?type=post", wait_until="domcontentloaded")
            page.wait_for_function("window.tinymce && tinymce.activeEditor && tinymce.activeEditor.initialized", timeout=30000)
            time.sleep(1)
            ok = page.evaluate("""h => { const e = tinymce.activeEditor, b = e.getBody();
                const p = [...b.querySelectorAll('p')].find(x => x.textContent.includes('AI가 뒤집어놓은 수학계 시리즈'));
                if (!p) return false;
                p.parentNode.outerHTML = h; e.undoManager.add(); e.setDirty(true); return true; }""", html)
            if not ok:
                print(k, "시리즈 표를 못 찾음, 건너뜀"); continue
            page.click("#publish-layer-btn")
            page.wait_for_selector(VIS["public"], state="attached", timeout=10000)
            if not page.is_checked(VIS["public"]):
                page.click(f"label[for={VIS['public'][1:]}] .checkbox-text")
            with page.expect_navigation(timeout=60000):
                page.click("#publish-btn")
            time.sleep(2)
            print(k, "시리즈 링크 반영:", info["url"])
        save_state(ctx); ctx.close()


if __name__ == "__main__":
    main()
