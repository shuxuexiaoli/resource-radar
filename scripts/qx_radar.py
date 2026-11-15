#!/usr/bin/env python3
"""QX 资源雷达（跑在 GitHub Actions 里）。

1. 监控四个上游 QX 仓库的新提交，把新脚本文件名摘进 candidates/qx-candidates.md；
2. 搜索 GitHub 上新的高星 QuantumultX 仓库，追加到候选清单。
去重状态存 state/qx-state.json（由工作流每天提交回仓库）。
只用标准库；有 GITHUB_TOKEN 时用它调 API（限额更高）。
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(ROOT, "state", "qx-state.json")
CAND_PATH = os.path.join(ROOT, "candidates", "qx-candidates.md")
WATCH = [
    "deezertidal/QuantumultX-Rewrite",
    "yqc007/QuantumultX",
    "NobyDa/Script",
    "Sliverkiss/QuantumultX",
]
CST = timezone(timedelta(hours=8))


def gh(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "resource-radar"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(API + path, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            last_err = e
            print(f"retry {attempt + 1}/3 for {path}: {e}")
    raise last_err


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    today = datetime.now(CST).strftime("%Y-%m-%d")
    state = load_state()
    commits_state = state.get("commits", {})
    seen_repos = set(state.get("seen_repos", []))
    baseline = not commits_state
    updates = []
    for repo in WATCH:
        try:
            commits = gh(f"/repos/{repo}/commits?per_page=15")
        except Exception as e:
            print(f"WARN: {repo} commits failed: {e}")
            continue
        if not commits:
            continue
        newest = commits[0]["sha"]
        old = commits_state.get(repo)
        commits_state[repo] = newest
        if baseline or not old or old == newest:
            continue
        for c in commits:
            if c["sha"] == old:
                break
            try:
                detail = gh(f"/repos/{repo}/commits/{c['sha']}")
            except Exception as e:
                print(f"WARN: {repo} commit detail failed: {e}")
                continue
            files = [f["filename"] for f in detail.get("files", [])]
            interesting = [
                f for f in files if f.endswith((".conf", ".js", ".json", ".snippet"))
            ]
            msg = c["commit"]["message"].split("\n")[0][:80]
            if interesting:
                updates.append(
                    f"- [{repo}] {msg}（{c['sha'][:7]}）：{', '.join(interesting[:10])}"
                )
            else:
                updates.append(
                    f"- [{repo}] {msg}（{c['sha'][:7]}）：{len(files)} 个文件变更"
                )

    known_text = ""
    if os.path.exists(CAND_PATH):
        known_text = open(CAND_PATH, encoding="utf-8").read()
    new_repos = []
    for q in ["QuantumultX", '"Quantumult X" rewrite']:
        try:
            res = gh(
                "/search/repositories?q="
                + urllib.parse.quote(q)
                + "+stars:>=100&sort=updated&order=desc&per_page=20"
            )
        except Exception as e:
            print(f"WARN: search failed: {e}")
            continue
        for item in res.get("items", []):
            fn = item["full_name"]
            if fn in seen_repos or fn in known_text or fn in WATCH:
                continue
            seen_repos.add(fn)
            desc = (item.get("description") or "无描述")[:100]
            new_repos.append(f"- {fn}（★{item['stargazers_count']}）：{desc}")

    if updates or new_repos:
        os.makedirs(os.path.dirname(CAND_PATH), exist_ok=True)
        with open(CAND_PATH, "a", encoding="utf-8") as f:
            if updates:
                f.write(f"\n## {today} 上游更新\n\n" + "\n".join(updates) + "\n")
            if new_repos:
                f.write(f"\n## {today} 新仓库候选\n\n" + "\n".join(new_repos) + "\n")

    state["commits"] = commits_state
    state["seen_repos"] = sorted(seen_repos)
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    print(
        f"done: {len(updates)} upstream updates, {len(new_repos)} new repos, "
        f"baseline={baseline}"
    )


if __name__ == "__main__":
    main()
