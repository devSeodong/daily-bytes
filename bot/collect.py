#!/usr/bin/env python3
"""19:00 리서치 수집. last30days + Brave 뉴스 + GitHub 신규 인기 레포를 모아
카테고리별 상위 항목만 담은 작은 research.json을 만든다. (AI가 읽는 건 이 파일 하나)

python3.12 collect.py [--date YYYY-MM-DD] [--days 7]
"""
import argparse, datetime as dt, json, os, subprocess, urllib.parse, urllib.request
from config import LAST30, LAST30_ENV, PY, day_dir, notify

QUERIES = {
    "ai-issue":  ["AI news this week", "LLM model release", "AI policy regulation"],
    "ai-trend":  ["trending AI github repo", "AI agent open source"],
    "dev-issue": ["end of life software release", "major framework release developer"],
}
BRAVE_Q = {
    "ai-issue":  ["AI model launch", "인공지능 발표"],
    "dev-issue": ["end of life support ends", "major release developers"],
}
L30_CHARS = 5000   # 쿼리당 last30days 결과를 이만큼만 남김
TOP = 8


def load_env():
    env = dict(os.environ)
    if LAST30_ENV.exists():
        for line in LAST30_ENV.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def get_json(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "daily-bytes-bot", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def last30(query, days, env):
    cmd = [PY, str(LAST30), "--days", str(days), "--store", "--emit", "compact", "--quick", query]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env).stdout
    except subprocess.TimeoutExpired:
        return {"query": query, "error": "timeout"}
    return {"query": query, "text": out.strip()[:L30_CHARS]}


def brave(query, env, days):
    key = env.get("BRAVE_API_KEY")
    if not key:
        return []
    fresh = "pw" if days <= 7 else "pm"
    url = "https://api.search.brave.com/res/v1/news/search?" + urllib.parse.urlencode({"q": query, "count": 10, "freshness": fresh})
    try:
        data = get_json(url, {"X-Subscription-Token": key, "Accept": "application/json"})
    except Exception as e:
        return [{"error": str(e)[:200]}]
    return [{"title": r.get("title"), "url": r.get("url"), "age": r.get("age"),
             "source": (r.get("meta_url") or {}).get("hostname"), "desc": (r.get("description") or "")[:240]}
            for r in data.get("results", [])[:TOP]]


def github_new(days):
    """최근 N일 안에 만들어진 AI 관련 레포를 스타 순으로."""
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    out = []
    for topic in ["llm", "ai-agent", "machine-learning", "mcp"]:
        q = f"topic:{topic} created:>={since}"
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc", "per_page": 10})
        try:
            for r in get_json(url).get("items", []):
                out.append({"repo": r["full_name"], "url": r["html_url"], "stars": r["stargazers_count"],
                            "lang": r.get("language"), "created": r["created_at"][:10], "desc": (r.get("description") or "")[:200]})
        except Exception as e:
            out.append({"error": f"{topic}: {str(e)[:150]}"})
    seen, uniq = set(), []
    for r in sorted([x for x in out if "repo" in x], key=lambda x: -x["stars"]):
        if r["repo"] not in seen:
            seen.add(r["repo"]); uniq.append(r)
    return uniq[:TOP + 4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--skip-last30", action="store_true")
    a = ap.parse_args()
    env = load_env()
    res = {"date": a.date, "days": a.days, "generated": dt.datetime.now().isoformat(timespec="seconds"), "categories": {}}
    for cat, qs in QUERIES.items():
        c = {"last30days": [] if a.skip_last30 else [last30(q, a.days, env) for q in qs],
             "brave_news": [x for q in BRAVE_Q.get(cat, []) for x in brave(q, env, a.days)]}
        if cat == "ai-trend":
            c["github_new_repos"] = github_new(a.days)
        res["categories"][cat] = c
    out = day_dir(a.date) / "research.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    kb = out.stat().st_size // 1024
    print(f"{out} ({kb} KB)")
    if kb < 2:
        notify("daily-bytes 수집 경고", f"{a.date} 리서치 결과가 거의 비어 있어요 ({kb} KB)")


if __name__ == "__main__":
    main()
