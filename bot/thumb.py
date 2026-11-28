#!/usr/bin/env python3
"""대표 이미지(1200x630) 생성. 픽셀 그리드 틀은 고정, 제목만 바뀐다.

python3.12 thumb.py --date 2026-11-26            # work/<date>/drafts/*.html 전부
python3.12 thumb.py --cat 01-ai-issue --title "줄1|줄2|줄3" --date 2026-11-26 --out x.png
커버 문구는 초안의 <!-- 커버: 줄1 | 줄2 | 줄3 --> 를 쓰고, 없으면 제목의 ' - ' 뒤를 자동 줄바꿈.
"""
import argparse, os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from config import CATS, cat, day_dir, read_meta

W, H = 1200, 630
BG = (15, 23, 42)
FONT_DIRS = [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path("/usr/share/fonts/truetype/noto")]
FONT_CANDIDATES = [
    os.environ.get("DB_FONT", ""),
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]


def noto(size, style):
    """기존 대표 이미지와 같은 Noto Sans KR이 설치돼 있으면 우선 사용 (정적 Bold/Regular 파일 또는 가변 폰트)."""
    for d in FONT_DIRS:
        f = d / f"NotoSansKR-{style}.ttf"
        if f.exists():
            return ImageFont.truetype(str(f), size)
        for v in list(d.glob("NotoSansKR*wght*.ttf")) + list(d.glob("NotoSansKR-VariableFont*.ttf")):
            try:
                font_ = ImageFont.truetype(str(v), size)
                font_.set_variation_by_name(style)
                return font_
            except Exception:
                continue
    return None


def font(size, bold=True, weight=None):
    f = noto(size, "Bold" if bold else "Regular")
    if f:
        return f
    for p in FONT_CANDIDATES:
        if p and Path(p).exists():
            if p.endswith(".ttc"):
                # ttc 안에서 이름으로 면을 찾음. Apple SD Gothic Neo는 Noto보다 얇아 제목은 ExtraBold로
                want = weight or ("Bold" if bold else "Regular")
                for i in range(32):
                    try:
                        f = ImageFont.truetype(p, size, index=i)
                    except OSError:
                        break
                    fam, style = f.getname()
                    if style == want and not fam.startswith("."):
                        return f
                return ImageFont.truetype(p, size, index=0)
            return ImageFont.truetype(p, size)
    raise SystemExit("한글 폰트를 찾지 못했어요. Noto Sans KR을 설치하거나 DB_FONT 환경변수로 지정해 주세요.")


def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wrap(text, f, maxw, draw, maxlines=3):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]; lines[-1] = lines[-1].rstrip(",") + "…"
    return lines


def render(cat_key, lines_or_title, date, out):
    c = cat(cat_key); col = hex2rgb(c["color"])
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):  # 픽셀 그리드 (빛 번짐 아래에 깔림)
        d.line([(x, 0), (x, H)], fill=(24, 33, 52))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(24, 33, 52))
    # 오른쪽 위 빛 번짐: 카테고리 색 원을 흐리게 덮음
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((780, 30, 1160, 410), fill=150)
    md.ellipse((880, 130, 1060, 310), fill=235)   # 가운데가 더 밝게
    mask = mask.filter(ImageFilter.GaussianBlur(85))
    tint = Image.new("RGB", (W, H), tuple(int(BG[i] * 0.35 + col[i] * 0.65) for i in range(3)))
    img = Image.composite(tint, img, mask)
    d = ImageDraw.Draw(img)
    # 카테고리 알약 + 날짜
    f_pill = font(26); pw = d.textlength(c["label"], font=f_pill) + 48
    d.rounded_rectangle((80, 70, 80 + pw, 124), radius=27, fill=col)
    d.text((104, 97), c["label"], font=f_pill, fill="white", anchor="lm")
    d.text((80 + pw + 22, 97), date.replace("-", "."), font=font(24, False), fill=(148, 163, 184), anchor="lm")
    d.text((80, 210), c["head"], font=font(36), fill=col, anchor="lm")
    f_t = font(54, weight="ExtraBold")
    if isinstance(lines_or_title, list):
        lines = [l for l in lines_or_title if l][:3]
    else:
        lines = wrap(lines_or_title, f_t, 820, d)
    y = 290
    for l in lines:
        d.text((80, y), l, font=f_t, fill="white", anchor="lm"); y += 68
    d.text((80, 565), "서동이의 코딩일기 · 오늘의 IT", font=font(22, False), fill=(148, 163, 184), anchor="lm")
    img.save(out, "PNG", optimize=True)
    return out


def cover_text(meta):
    if meta.get("커버"):
        return [s.strip() for s in meta["커버"].split("|")]
    t = meta.get("제목", "")
    return t.split(" - ", 1)[1] if " - " in t else t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--cat"); ap.add_argument("--title"); ap.add_argument("--out")
    a = ap.parse_args()
    if a.cat:
        print(render(a.cat, a.title.split("|") if "|" in a.title else a.title, a.date, a.out or f"{a.cat}.png")); return
    d = day_dir(a.date); (d / "covers").mkdir(exist_ok=True)
    for f in sorted((d / "drafts").glob("*.html")):
        if cat(f.stem):
            out = d / "covers" / f"{f.stem}-cover.png"
            if out.exists() and out.stat().st_mtime >= f.stat().st_mtime:
                print(f"{out} (이미 있음)"); continue
            meta = read_meta(f.read_text(encoding="utf-8"))
            print(render(f.stem, cover_text(meta), a.date, out))


if __name__ == "__main__":
    main()
