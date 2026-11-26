#!/usr/bin/env python3
"""20:00 티스토리 발행. Playwright 전용 프로필의 로그인 세션을 재사용한다.

python3.12 publish.py --date 2026-11-26                 # 공개 발행 (work/<date>/drafts/*.html)
python3.12 publish.py --date 2026-11-26 --visibility private   # 비공개 테스트
python3.12 publish.py --login        # 로그인 창 열기 (카카오 QR 화면을 work/login-qr.png 로 저장)
python3.12 publish.py --check        # 로그인 살아 있는지만 확인 (0=OK, 2=만료)

결과는 work/<date>/published.json. 이미 발행한 글은 건너뛴다(재실행 안전).
"""
import argparse, base64, json, re, sys, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from config import BLOG, BOT, CATS, PROFILE, day_dir, notify, read_meta, strip_meta

VIS = {"public": "#open20", "protected": "#open15", "private": "#open0"}


def browser(p, headless=False):
    PROFILE.mkdir(parents=True, exist_ok=True)
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=headless, locale="ko-KR",
                                               viewport={"width": 1400, "height": 1000})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.on("dialog", lambda d: d.dismiss())   # "작성 중인 글이 있어요, 이어서?" → 새로 쓰기
    return ctx, page


def logged_in(page):
    page.goto(f"{BLOG}/manage/posts", wait_until="domcontentloaded")
    time.sleep(2)
    return "/manage" in page.url and "login" not in page.url


def do_login(p):
    ctx, page = browser(p)
    page.goto("https://www.tistory.com/auth/login", wait_until="domcontentloaded")
    try:
        page.click("a.btn_login.link_kakao_id", timeout=8000)
    except PWTimeout:
        pass
    time.sleep(3)
    try:  # 카카오 QR 로그인 탭 + 로그인 상태 유지
        page.get_by_text("QR코드 로그인").first.click(timeout=5000)
        time.sleep(2)
    except PWTimeout:
        pass
    shot = BOT / "work" / "login-qr.png"; shot.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(shot))
    print(f"QR 화면: {shot}  (카카오톡으로 스캔하면 됩니다. 5분 기다려요)")
    for _ in range(60):
        time.sleep(5)
        if "tistory.com" in page.url and "login" not in page.url:
            print("로그인 완료"); break
    ok = logged_in(page); ctx.close()
    return ok


def set_body(page, html, cover_png):
    page.wait_for_function("window.tinymce && tinymce.activeEditor && tinymce.activeEditor.initialized", timeout=30000)
    page.evaluate("h => { const e = tinymce.activeEditor; e.setContent(h); e.undoManager.add(); }", html)
    if cover_png:
        b64 = base64.b64encode(cover_png.read_bytes()).decode()
        # 맨 위에 커서를 두고 이미지 파일을 붙여넣기 → 티스토리가 직접 업로드
        page.evaluate("""async (b64) => {
          const e = tinymce.activeEditor, body = e.getBody();
          const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
          const file = new File([bin], 'cover.png', {type: 'image/png'});
          const p = e.dom.create('p', {}, '<br>'); body.insertBefore(p, body.firstChild);
          e.selection.setCursorLocation(p, 0); e.focus();
          const dt = new DataTransfer(); dt.items.add(file);
          body.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
        }""", b64)
        page.wait_for_function("tinymce.activeEditor.getContent().includes('[##_Image')", timeout=60000)
        try:  # 이미지의 '대표' 버튼 (없으면 첫 이미지가 대표가 됨)
            fr = page.frame_locator("iframe#editor-tistory_ifr")
            fr.locator("img").first.click(timeout=5000)
            page.get_by_text("대표", exact=True).first.click(timeout=5000)
        except Exception:
            pass


def pick_category(page, label):
    page.click("#category-btn")
    items = page.locator("#category-list .mce-menu-item, #category-list [role=option]")
    n = items.count()
    for i in range(n):
        if items.nth(i).inner_text().strip().lstrip("- ").strip() == label:
            items.nth(i).click(); return
    raise RuntimeError(f"카테고리 '{label}'를 찾지 못했어요")


def add_tags(page, tags):
    box = page.locator("#tagText")
    for t in tags:
        box.fill(t); box.press("Enter"); time.sleep(0.2)


def publish_one(page, key, draft, cover, vis):
    raw = draft.read_text(encoding="utf-8")
    meta = read_meta(raw)
    title, tags = meta.get("제목"), [t.strip() for t in meta.get("태그", "").split(",") if t.strip()]
    if not title or not tags:
        raise RuntimeError(f"{draft.name}: <!-- 제목 --> / <!-- 태그 --> 주석이 필요해요")
    page.goto(f"{BLOG}/manage/newpost/?type=post", wait_until="domcontentloaded")
    page.wait_for_selector("#post-title-inp", timeout=30000)
    pick_category(page, CATS[key]["label"])
    page.fill("#post-title-inp", title)
    set_body(page, strip_meta(raw), cover if cover.exists() else None)
    add_tags(page, tags)
    page.click("#publish-layer-btn")
    page.click(VIS[vis], timeout=10000)
    with page.expect_navigation(timeout=60000):
        page.click("#publish-btn")
    time.sleep(3)
    # 방금 쓴 글 주소 찾기 (관리 목록 첫 글 중 제목 일치)
    page.goto(f"{BLOG}/manage/posts", wait_until="domcontentloaded"); time.sleep(2)
    url = page.evaluate("""t => { for (const a of document.querySelectorAll('a[href]')) {
        if (a.textContent.trim() === t && /\\/\\d+$/.test(a.href)) return a.href; } return null; }""", title)
    return {"title": title, "tags": tags, "url": url, "visibility": vis}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date"); ap.add_argument("--visibility", choices=list(VIS), default="public")
    ap.add_argument("--login", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", help="예: 01-ai-issue")
    a = ap.parse_args()
    with sync_playwright() as p:
        if a.login:
            sys.exit(0 if do_login(p) else 2)
        ctx, page = browser(p)
        if not logged_in(page):
            ctx.close()
            notify("티스토리 로그인 만료", "맥 미니에서 다시 로그인이 필요해요 (publish.py --login)")
            sys.exit(2)
        if a.check:
            ctx.close(); print("로그인 OK"); return
        d = day_dir(a.date); out = d / "published.json"
        done = json.loads(out.read_text()) if out.exists() else {}
        drafts = sorted((d / "drafts").glob("*.html"))
        if not drafts:
            notify("daily-bytes 발행 보류", f"{a.date} 초안이 없어요"); sys.exit(3)
        errors = []
        for f in drafts:
            key = f.stem
            if key not in CATS or (a.only and key != a.only) or key in done:
                continue
            try:
                done[key] = publish_one(page, key, f, d / "covers" / f"{key}-cover.png", a.visibility)
                out.write_text(json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")
                print(key, done[key]["url"])
            except Exception as e:
                page.screenshot(path=str(d / f"error-{key}.png"))
                errors.append(f"{key}: {str(e)[:200]}")
        ctx.close()
        if errors:
            notify("daily-bytes 발행 실패", " / ".join(errors)); sys.exit(1)


if __name__ == "__main__":
    main()
