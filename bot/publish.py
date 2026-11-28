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
from config import BLOG, BOT, CATS, PROFILE, cat, day_dir, notify, read_meta, strip_meta, todays_key

VIS = {"public": "#open20", "protected": "#open15", "private": "#open0"}
STATE = BOT / "state.json"   # 로그인 쿠키 백업 (권한 600). 세션 쿠키도 브라우저 재시작 뒤 되살린다.
KEEP_DAYS = 30


def save_state(ctx):
    """현재 쿠키를 state.json에 백업. 세션 쿠키(만료 없음)는 KEEP_DAYS 뒤 만료로 바꿔 저장."""
    st = ctx.storage_state()
    until = time.time() + KEEP_DAYS * 86400
    for c in st.get("cookies", []):
        if c.get("expires", -1) in (-1, None) or c["expires"] < 0:
            c["expires"] = until
    STATE.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
    STATE.chmod(0o600)


def restore_state(ctx):
    if not STATE.exists():
        return
    try:
        cookies = json.loads(STATE.read_text(encoding="utf-8")).get("cookies", [])
        now = time.time()
        ctx.add_cookies([c for c in cookies if c.get("expires", now + 1) > now])
    except Exception as e:
        print("state.json 복원 실패:", e, flush=True)


def browser(p, headless=False):
    PROFILE.mkdir(parents=True, exist_ok=True)
    ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=headless, locale="ko-KR",
                                               viewport={"width": 1400, "height": 1000})
    restore_state(ctx)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.on("dialog", lambda d: d.dismiss())   # "작성 중인 글이 있어요, 이어서?" → 새로 쓰기
    return ctx, page


def logged_in(page):
    # 비로그인이면 JS로 늦게 로그인 페이지로 튕기므로 충분히 기다린 뒤, 관리 화면 요소까지 확인
    page.goto(f"{BLOG}/manage/posts", wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PWTimeout:
        pass
    time.sleep(3)
    if "login" in page.url or "/manage" not in page.url:
        return False
    return page.locator("a[href*='/manage/post']").count() > 0


STAY_TXT = "로그인 상태 유지"


def stay_box(page):
    """'로그인 상태 유지' 체크박스 locator. 카카오가 id/name을 바꿔도 라벨 글자로 찾아낸다."""
    for sel in ("input[name='staySignedIn']", "input[name='stay_signed_in']",
                "input[id^='staySignedIn']", "input#staySignedIn"):
        box = page.locator(sel).first
        try:
            if box.count():
                return box
        except Exception:
            pass
    # 전용 라벨 id → for 속성 → 그 input
    try:
        lab = page.locator("#label-staySignedIn").first
        if not lab.count():
            lab = page.locator(f"label:has-text('{STAY_TXT}')").first
        if lab.count():
            fid = lab.get_attribute("for")
            if fid:
                box = page.locator(f"#{fid}").first
                if box.count():
                    return box
            box = lab.locator("input[type=checkbox]").first
            if box.count():
                return box
    except Exception:
        pass
    return None


def ensure_stay(page):
    """'로그인 상태 유지'를 켠다. QR 탭을 누른 '뒤에' 불러야 한다.

    2026-11-28 확인: QR 탭 이전 화면에는 이 체크박스가 아예 없다
    (그 화면의 체크박스는 name=saveSignedIn '간편로그인 정보 저장'으로 다른 것이다).
    QR 탭을 누른 뒤에 name=staySignedIn, id=staySignedIn--1, 라벨 id=label-staySignedIn 으로 나타난다.
    """
    box = stay_box(page)
    if box is None:
        print("로그인 상태 유지: 체크박스를 못 찾음", flush=True)
        return False
    try:
        if box.is_checked():
            print("로그인 상태 유지: True (이미 켜져 있음)", flush=True)
            return True
    except Exception:
        pass
    attempts = [
        ("id label click", lambda: page.locator("#label-staySignedIn").first.click(timeout=3000)),
        ("check()", lambda: box.check(timeout=3000, force=True)),
        ("label click", lambda: page.locator(f"label:has-text('{STAY_TXT}')").first.click(timeout=3000)),
        ("input click", lambda: box.click(timeout=3000, force=True)),
        ("js click", lambda: box.evaluate("el => el.click()")),
        ("js set+event", lambda: box.evaluate(
            "el => { el.checked = true;"
            " el.dispatchEvent(new Event('input', {bubbles:true}));"
            " el.dispatchEvent(new Event('change', {bubbles:true})); }")),
    ]
    for name, fn in attempts:
        try:
            fn()
        except Exception as e:
            print(f"로그인 상태 유지: {name} 실패 ({type(e).__name__})", flush=True)
            continue
        try:
            if box.is_checked():
                print(f"로그인 상태 유지: True ({name})", flush=True)
                return True
        except Exception:
            pass
        print(f"로그인 상태 유지: {name} 눌렀지만 체크 안 됨", flush=True)
    try:   # 다음 로그인 때 원인을 바로 알 수 있게 DOM을 남긴다
        print("체크박스 DOM:", box.evaluate("el => el.outerHTML")[:300], flush=True)
        print("라벨 DOM:", page.locator(f"label:has-text('{STAY_TXT}')").first
              .evaluate("el => el.outerHTML")[:300], flush=True)
    except Exception:
        pass
    return False


def force_stay_url(page):
    """체크박스가 안 먹었을 때: QR 주소의 append_stay_signed_in=false 를 true 로 바꿔 다시 띄운다."""
    if "append_stay_signed_in=false" not in page.url:
        return False
    url = page.url.replace("append_stay_signed_in=false", "append_stay_signed_in=true")
    try:
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(2)
        ok = "append_stay_signed_in=true" in page.url
        print("QR 주소 보정:", "성공" if ok else f"실패 ({page.url[:120]})", flush=True)
        return ok
    except Exception as e:
        print("QR 주소 보정 실패:", e, flush=True)
        return False


def open_qr_tab(page):
    """QR 로그인 탭을 누르고, 화면이 QR 화면으로 바뀔 때까지 기다린다.

    주소는 20초 넘게 accounts.kakao.com/login/ 그대로이고 화면 안에서만 바뀌므로,
    주소가 아니라 '로그인 상태 유지' 체크박스가 나타나는 것을 기준으로 삼는다 (2026-11-28 확인).
    """
    try:
        page.get_by_text("QR코드 로그인").first.click(timeout=5000)
    except PWTimeout:
        pass
    for _ in range(30):          # 최대 15초
        if stay_box(page) is not None:
            time.sleep(0.5)
            return True
        time.sleep(0.5)
    print("QR 화면으로 바뀌지 않았어요:", page.url[:120], flush=True)
    return False


def reissue_qr(page):
    """상태 유지를 켠 뒤 QR을 다시 발급받는다. 먼저 뜬 QR에는 그 값이 안 담길 수 있다."""
    for sel in ("button[aria-label*='새로고침']", "button:has-text('새로고침')",
                "a:has-text('새로고침')", "button.btn_refresh", ".btn_refresh",
                "button[class*='refresh']"):
        try:
            btn = page.locator(sel).first
            if btn.count():
                btn.click(timeout=3000)
                time.sleep(2)
                print(f"QR 재발급: {sel}", flush=True)
                return True
        except Exception:
            continue
    print("QR 재발급: 새로고침 버튼을 못 찾음 (떠 있는 QR을 그대로 씁니다)", flush=True)
    return False


def do_login(p):
    try:
        ctx, page = browser(p)
    except Exception as e:
        # 앞서 띄운 로그인 브라우저가 아직 프로필을 쓰고 있으면 여기서 바로 죽는다.
        print("로그인 창을 열 수 없어요. 이미 열려 있는 로그인 브라우저를 먼저 닫아 주세요.", flush=True)
        print("  원인:", type(e).__name__, str(e)[:200], flush=True)
        return False
    page.goto("https://www.tistory.com/auth/login", wait_until="domcontentloaded")
    try:
        page.click("a.btn_login.link_kakao_id", timeout=8000)
    except PWTimeout:
        pass
    time.sleep(3)
    # 순서가 중요하다. '로그인 상태 유지' 체크박스는 QR 탭을 누른 뒤에만 존재한다.
    # 체크하지 않으면 서버가 세션을 짧게 잡아 반나절 만에 로그인이 풀린다 (2026-11-27, 11-28 확인).
    open_qr_tab(page)
    if ensure_stay(page):
        reissue_qr(page)        # 먼저 뜬 QR에는 상태 유지가 안 담겼을 수 있다
    elif "append_stay_signed_in=false" in page.url:
        force_stay_url(page)    # 주소가 이미 QR 쪽으로 바뀌어 있으면 주소로 보정해 본다
    print("QR 주소 상태 유지:",
          "true" if "append_stay_signed_in=true" in page.url else page.url[:120], flush=True)
    shot = BOT / "work" / "login-qr.png"; shot.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(shot))
    expiry = time.strftime("%H:%M:%S", time.localtime(time.time() + 300))
    print(f"QR 화면: {shot}  (카카오톡으로 스캔, {expiry}까지 유효)", flush=True)
    try:  # 원격에서 보낼 수 있게 QR 내용도 텍스트로 (opencv 있으면)
        import cv2
        txt, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(shot)))
        if txt:
            (BOT / "work" / "login-qr.txt").write_text(f"{txt}\n{expiry}\n", encoding="utf-8")
            print("QR 텍스트: work/login-qr.txt", flush=True)
    except Exception:
        pass
    last = None
    for i in range(60):
        time.sleep(5)
        if page.url != last:
            last = page.url; print(f"[{i*5}s] {last[:120]}", flush=True)
        if "tistory.com" in page.url and "login" not in page.url:
            print("로그인 완료", flush=True); break
    page.screenshot(path=str(BOT / "work" / "login-last.png"))
    ok = logged_in(page)
    print("logged_in:", ok, page.url[:120], flush=True)
    if ok:
        save_state(ctx)
    ctx.close()
    if not ok:
        return False
    # 브라우저를 껐다 켜도 살아 있는지 확인 (매일 발행은 새 브라우저로 시작하므로)
    ctx, page = browser(p)
    ok = logged_in(page)
    print("재시작 후 logged_in:", ok, flush=True)
    if ok:
        save_state(ctx)
    ctx.close()
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
    pick_category(page, cat(key)["label"])
    page.fill("#post-title-inp", title)
    set_body(page, strip_meta(raw), cover if cover.exists() else None)
    add_tags(page, tags)
    page.click("#publish-layer-btn")
    page.wait_for_selector(VIS[vis], state="attached", timeout=10000)
    # 라디오 input/label은 높이 0이라 안쪽 글자(span)를 누름
    page.click(f"label[for={VIS[vis][1:]}] .checkbox-text")
    if not page.is_checked(VIS[vis]):
        raise RuntimeError(f"공개 범위 {vis} 선택 실패")
    if cover.exists():  # 발행 창의 '대표이미지 추가'에 커버 업로드
        page.set_input_files(".box_thumb input[type=file]", str(cover))
        # 업로드가 끝나면 '대표이미지 추가' 안내 글자가 사라지고 미리보기가 뜸
        page.wait_for_selector(".box_thumb .txt_thumb", state="hidden", timeout=30000)
        time.sleep(1)
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
    ap.add_argument("--only", help="예: 01-ai-issue (기본: 그날 요일의 카테고리 하나)")
    ap.add_argument("--all", action="store_true", help="요일 상관없이 drafts의 모든 초안 발행")
    a = ap.parse_args()
    if a.date and not (a.only or a.all or a.login or a.check):
        a.only = todays_key(a.date)
        if a.only is None:
            print(f"{a.date} 일요일 휴재 → 발행 안 함"); return
    with sync_playwright() as p:
        if a.login:
            sys.exit(0 if do_login(p) else 2)
        ctx, page = browser(p)
        if not logged_in(page):
            ctx.close()
            notify("티스토리 로그인 만료", "맥 미니에서 다시 로그인이 필요해요 (publish.py --login)")
            sys.exit(2)
        save_state(ctx)   # 갱신된 쿠키 백업
        if a.check:
            ctx.close(); print("로그인 OK"); return
        d = day_dir(a.date); out = d / "published.json"
        done = json.loads(out.read_text()) if out.exists() else {}
        drafts = sorted((d / "drafts").glob("*.html"))
        if a.only:
            drafts = [f for f in drafts if f.stem == a.only]
        if a.only and a.only in done:
            ctx.close(); print(f"{a.only} 이미 발행됨: {done[a.only].get('url')}"); return
        if not drafts:
            ctx.close()
            notify("daily-bytes 발행 보류", f"{a.date} 초안이 없어요 ({a.only or '전체'})"); sys.exit(3)
        errors = []
        for f in drafts:
            key = f.stem
            if cat(key) is None or (a.only and key != a.only) or key in done:
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
