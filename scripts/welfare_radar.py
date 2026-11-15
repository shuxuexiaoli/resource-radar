#!/usr/bin/env python3
"""linux.do 福利帖雷达（跑在 GitHub Actions 里）。

抓 linux.do 公开 RSS，按标题关键词筛资源类帖子（公益站、免费额度、免费订阅等），
新候选追加到 candidates/welfare-candidates.md。去重状态存 state/welfare-seen.txt。
抓不到（被拦等）就打印警告并正常退出，不让工作流变红。
只用标准库。
"""
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_PATH = os.path.join(ROOT, "state", "welfare-seen.txt")
CAND_PATH = os.path.join(ROOT, "candidates", "welfare-candidates.md")
CST = timezone(timedelta(hours=8))
KEYWORDS = [
    "公益站", "免费额度", "免费订阅", "机场", "签到", "福利站",
    "注册送", "新站", "不限量", "公益节点", "白嫖",
]
SOURCES = ["https://linux.do/latest.rss", "https://linux.do/c/welfare.rss"]
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    today = datetime.now(CST).strftime("%Y-%m-%d")
    seen = set()
    if os.path.exists(SEEN_PATH):
        seen = set(open(SEEN_PATH, encoding="utf-8").read().split())
    items = []
    ok = False
    for src in SOURCES:
        try:
            root = ET.fromstring(fetch(src))
            for it in root.iter("item"):
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                if title and link:
                    items.append((title, link))
            ok = True
            print(f"fetched {src}: {len(items)} items")
            break
        except Exception as e:
            print(f"WARN: {src} failed: {e}")
    if not ok:
        print("all RSS sources failed; nothing recorded")
        return

    hits = []
    for title, link in items:
        if link in seen:
            continue
        seen.add(link)
        if any(k in title for k in KEYWORDS):
            hits.append(f"- {title}｜{link}")

    if hits:
        os.makedirs(os.path.dirname(CAND_PATH), exist_ok=True)
        with open(CAND_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n## {today}\n\n" + "\n".join(hits) + "\n")
    os.makedirs(os.path.dirname(SEEN_PATH), exist_ok=True)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(seen)) + "\n")
    print(f"done: {len(hits)} keyword hits of {len(items)} items")


if __name__ == "__main__":
    main()
