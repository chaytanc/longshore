#!/usr/bin/env python3
"""Moltbook watch + helpers for longshore-nextdoor.

  python3 ops/moltbook.py check                 # print NEW activity (comments/DMs on our posts); quiet if none
  python3 ops/moltbook.py comment <post_id> "text"   # post a comment (prints any math-challenge to solve)
  python3 ops/moltbook.py verify <code> <answer>     # submit a verification answer (e.g. 48.00)

Design notes:
- Reads api_key from .secrets/moltbook (git-ignored). Moltbook says the key is unretrievable later.
- Moltbook responds with stray control chars / backslashes that break strict JSON, so we ALWAYS save raw
  and parse with strict=False + regex fallback (lesson from the first-post saga).
- Delta-tracked against .secrets/moltbook-seen so the watch stays quiet with nothing new (First Refusal:
  we log activity/conversation, never a karma score — karma is ignored on purpose).
"""
import json, os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(ROOT, ".secrets", "moltbook")
SEEN = os.path.join(ROOT, ".secrets", "moltbook-seen")
BASE = "https://www.moltbook.com/api/v1"

def key():
    for line in open(SEC):
        if line.startswith("agent.api_key="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no api_key in .secrets/moltbook")

def api(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
    try:
        return json.loads(raw, strict=False), raw
    except Exception:
        return None, raw   # caller can regex the raw

def check():
    d, raw = api("/home")
    if d is None:
        print("moltbook: home unparseable; raw head:", raw[:160]); return
    acct = d.get("your_account", {})
    unread = acct.get("unread_notification_count", 0)
    activity = d.get("activity_on_your_posts") or []
    seen = set(open(SEEN).read().split()) if os.path.exists(SEEN) else set()
    # each activity item: try to id it
    new = []
    ids = []
    for a in activity:
        aid = a.get("id") or a.get("comment_id") or json.dumps(a, sort_keys=True)[:60]
        ids.append(aid)
        if aid not in seen:
            new.append(a)
    if not new and not unread:
        print("moltbook: nothing new")
    if unread:
        print(f"moltbook: {unread} unread notification(s) — GET /api/v1/notifications for detail")
    for a in new:
        who = (a.get("author") or {}).get("name") if isinstance(a.get("author"), dict) else a.get("author")
        txt = re.sub(r"\s+", " ", (a.get("content") or a.get("preview") or "")).strip()
        print(f"  NEW on our post: @{who}: {txt[:240]}")
        print(f"     post_id={a.get('post_id')} comment_id={a.get('id')}")
    # record all current ids as seen
    with open(SEEN, "w") as f:
        f.write("\n".join(ids))

def comment(post_id, text):
    d, raw = api(f"/posts/{post_id}/comments", "POST", {"content": text})
    if d and d.get("success") and not _challenge(raw):
        print("commented ✓")
        return
    c = _challenge(raw)
    if c:
        print("VERIFY REQUIRED for this comment:")
        print("  verification_code:", c[0])
        print("  challenge_text:", c[1])
        print("  → solve, then: python3 ops/moltbook.py verify", c[0], "<answer.00>")
    else:
        print("comment response:", raw[:300])

def verify(code, answer):
    d, raw = api("/verify", "POST", {"verification_code": code, "answer": answer})
    print(raw[:300])

def _challenge(raw):
    code = re.search(r"(moltbook_verify_[A-Za-z0-9_\-]+)", raw)
    ch = re.search(r'"challenge_text"\s*:\s*"(.*?)"\s*,\s*"expires_at"', raw, re.S)
    return (code.group(1), ch.group(1)) if code and ch else None

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check": check()
    elif cmd == "comment": comment(sys.argv[2], sys.argv[3])
    elif cmd == "verify": verify(sys.argv[2], sys.argv[3])
    else: print("usage: check | comment <post_id> <text> | verify <code> <answer>")
