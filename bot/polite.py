#!/usr/bin/env python3
"""글 말투 검사·교정. 평어체("~한다")를 존댓말("~합니다")로 바꾸고 "~요" 종결을 잡아낸다.

python3 polite.py --check  work/2026-11-27/drafts/*.html   # 0=깨끗, 1=평어체/요체 발견
python3 polite.py --fix    work/2026-11-27/drafts/*.html    # 제자리 교정 (.bak 남김)

사용자 규칙: 본문은 존댓말(~합니다/~했습니다/~입니다), "~요" 종결(~해요, ~했고요)은 쓰지 않는다.
<pre> 코드블록과 마크다운 ``` 블록은 건드리지 않는다.
"""
import re, sys, shutil, pathlib

MAP = {
    "걸었다": "걸었습니다", "검토한다": "검토합니다", "공개됐다": "공개됐습니다", "나왔다": "나왔습니다",
    "낫다": "낫습니다", "동작한다": "동작합니다", "된다": "됩니다", "뜻이다": "뜻입니다",
    "들어갔다": "들어갔습니다", "들어왔다": "들어왔습니다", "띄운다": "띄웁니다", "띈다": "띕니다",
    "마지막이다": "마지막입니다", "많았다": "많았습니다", "맞았다": "맞았습니다", "못한다": "못합니다",
    "바뀌었다": "바뀌었습니다", "바뀐다": "바뀝니다", "밝혔다": "밝혔습니다", "배포됐다": "배포됐습니다",
    "버전이다": "버전입니다", "빨라졌다": "빨라졌습니다", "생겼다": "생겼습니다", "설정이다": "설정입니다",
    "셈이다": "셈입니다", "안전하다": "안전합니다", "않는다": "않습니다", "예정이다": "예정입니다",
    "올라간다": "올라갑니다", "있다": "있습니다", "없다": "없습니다", "재구성한다": "재구성합니다",
    "적었다": "적었습니다", "제거됐다": "제거됐습니다", "종료됐다": "종료됐습니다", "줄어든다": "줄어듭니다",
    "차이다": "차이입니다", "추가됐다": "추가됐습니다", "컴파일러다": "컴파일러입니다",
    "포함된다": "포함됩니다", "필요하다": "필요합니다", "하나다": "하나입니다", "한다": "합니다",
    "확인한다": "확인합니다", "올라온다": "올라옵니다", "쌓는다": "쌓습니다", "아니다": "아닙니다",
    "같다": "같습니다", "크다": "큽니다", "적다": "적습니다", "많다": "많습니다", "좋다": "좋습니다",
}
# 문장이 끝나는 자리만 고친다. 마침표, 또는 블록 태그가 닫히는 자리.
# "않는다고", "않는다</b>고" 처럼 문장 중간에 오는 형태는 건드리지 않는다.
END = r"(?=\s*(?:[.!?]|</(?:p|li|td|th|blockquote|h[1-6])>))"
PAT = re.compile("(" + "|".join(sorted(MAP, key=len, reverse=True)) + ")" + END)
# 사전에 없는 평어체를 놓치지 않도록, 문장 끝 "~다" 도 따로 경고한다.
PLAIN = re.compile(r"[가-힣]{1,8}(?<!니)다" + END)
# "~하나요?" 같은 의문문은 FAQ 제목에 필요하므로 물음표는 뺀다.
YO = re.compile(r"[가-힣]{1,6}요(?=\s*(?:[.!]|</(?:p|li|td|th|blockquote|h[1-6])>))")
SKIP = re.compile(r"(<pre\b.*?</pre>|```.*?```|<code\b.*?</code>)", re.S)


def split_skip(text):
    """(건드릴 조각, 건너뛸 조각) 순서대로 나눈 리스트."""
    return SKIP.split(text)


def fix(text):
    parts, n = split_skip(text), 0
    for i, part in enumerate(parts):
        if SKIP.fullmatch(part):
            continue
        parts[i], k = PAT.subn(lambda m: MAP[m.group(1)], part)
        n += k
    return "".join(parts), n


def check(text):
    body = "".join(p for p in split_skip(text) if not SKIP.fullmatch(p))
    plain = sorted(set(PLAIN.findall(body)) - {"습니다"})
    plain = [w for w in plain if not w.endswith("습니다")]
    return plain, sorted(set(YO.findall(body)))


def main(argv):
    if len(argv) < 2 or argv[0] not in ("--check", "--fix"):
        print(__doc__); return 2
    mode, paths, bad = argv[0], argv[1:], 0
    for s in paths:
        p = pathlib.Path(s)
        text = p.read_text(encoding="utf-8")
        if mode == "--fix":
            new, n = fix(text)
            if n:
                shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))
                p.write_text(new, encoding="utf-8")
            text = new
            print(f"{p.name}: {n}곳 교정")
        plain, yo = check(text)
        if plain or yo:
            bad = 1
            print(f"{p.name}: 평어체 {plain}  요체 {yo}")
        elif mode == "--check":
            print(f"{p.name}: 말투 OK")
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
