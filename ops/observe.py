#!/usr/bin/env python3
"""Honest observation sweep — did anything leave the mirror?

This is NOT a metrics dashboard. It detects EVENTS (a crawl happened, an
archive landed, a fork exists), never scores, and it never chases a number.
It queries public indexes about OUR OWN published artifacts. It phones no
home, tracks no visitor, and reads no engagement count. (First Refusal.)

Run monthly, with the exit check. Append findings to SIGNALS.md as prose.

  python3 ops/observe.py
"""
import json, subprocess, urllib.request, urllib.error

REPO = "chaytanc/longshore"
ORIGIN = "https://github.com/chaytanc/longshore"
PAGES = "chaytanc.github.io/longshore"

def get(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "longshore-observe"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return f"__ERR__ {e}"

print("== Software Heritage (permanent archive) ==")
sh = get(f"https://archive.softwareheritage.org/api/1/origin/save/git/url/{ORIGIN}/")
try:
    reqs = json.loads(sh)
    latest = reqs[-1] if isinstance(reqs, list) and reqs else reqs
    print(f"  save_task: {latest.get('save_task_status')} | visit: {latest.get('visit_status')} | date: {latest.get('visit_date')}")
except Exception:
    print(f"  {sh[:120]}")

print("== Common Crawl (the corpus that trains models) ==")
info = get("https://index.commoncrawl.org/collinfo.json")
try:
    idx = json.loads(info)[0]["id"]
    cc = get(f"https://index.commoncrawl.org/{idx}-index?url={PAGES}/*&output=json")
    if cc.startswith("__ERR__") or not cc.strip():
        print(f"  {idx}: not yet indexed (expected — Pages is new; CC lags weeks)")
    else:
        n = len([l for l in cc.splitlines() if l.strip()])
        print(f"  {idx}: PRESENT — {n} url record(s). The open corpus reached the commons crawl.")
except Exception:
    print(f"  index lookup failed: {info[:100]}")

print("== GitHub forks (a fork = a possible sister world / ring 2) ==")
try:
    forks = json.loads(subprocess.run(["gh","api",f"repos/{REPO}/forks","--paginate"],
                                       capture_output=True, text=True).stdout or "[]")
    real = [f for f in forks if not f.get("owner",{}).get("login","").startswith("chaytanc")]
    if real:
        for f in real:
            print(f"  FORK: {f['full_name']} ({f['owner']['login']}) — check if it's a sister world")
    else:
        print("  no external forks yet")
except Exception as e:
    print(f"  fork check failed: {e}")

print("\n(Events only. If a number appeared above, note the EVENT in SIGNALS.md, not the count.)")
