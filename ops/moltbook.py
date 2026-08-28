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
    # CI/durable-watch path: the GitHub Action injects the key as an env secret
    # (no .secrets/ file in a fresh checkout). Local path: read the git-ignored file.
    env = os.environ.get("MOLTBOOK_API_KEY")
    if env:
        return env.strip()
    if os.path.exists(SEC):
        for line in open(SEC):
            if line.startswith("agent.api_key="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("no api_key: set MOLTBOOK_API_KEY or .secrets/moltbook")

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
    # Read /notifications directly — it carries EVERY engagement type
    # (comment_reply, reply, mention, new_follower, ...). /home's
    # activity_on_your_posts only covers our own posts and MISSES replies to
    # our comments on others' threads, which is most of what we do.
    d, raw = api("/notifications?limit=40")
    if d is None:
        print("moltbook: notifications unparseable; raw head:", raw[:160]); return
    notes = d.get("notifications") or []
    seen = set(open(SEEN).read().split()) if os.path.exists(SEEN) else set()
    ids = [n.get("id") for n in notes if n.get("id")]
    new = [n for n in notes if n.get("id") and n.get("id") not in seen]
    if not new:
        print("moltbook: nothing new"); _persist_seen(ids); return
    print(f"moltbook: {len(new)} new notification(s):")
    for n in new:
        t = n.get("type", "?")
        post = n.get("post") or {}
        title = re.sub(r"\s+", " ", (post.get("title") or "")).strip()
        pid = n.get("relatedPostId") or post.get("id")
        cid = n.get("relatedCommentId")
        content = re.sub(r"\s+", " ", (n.get("content") or "")).strip()
        line = f"  [{t}] {content}"
        if title:
            line += f'  — on "{title[:70]}"'
        print(line)
        if t in ("comment_reply", "reply", "mention") and pid:
            # surface a jump + best-effort peek at the actual reply text
            print(f"     post_id={pid} comment_id={cid}")
            peek = _reply_text(pid, cid) if cid else None
            if peek is not None:
                print(f'     reply: "{peek[:240]}"' if peek else
                      "     (reply not found in thread — likely deleted/removed)")
    _persist_seen(ids)

def _persist_seen(ids):
    with open(SEEN, "w") as f:
        f.write("\n".join([i for i in ids if i]))

def _reply_text(post_id, comment_id):
    """Best-effort: find a specific comment's text in a thread (incl. nested replies)."""
    d, _ = api(f"/posts/{post_id}/comments?sort=new&limit=100")
    if not d:
        return None
    def walk(cs):
        for c in cs or []:
            if c.get("id") == comment_id:
                who = (c.get("author") or {}).get("name")
                return f"@{who}: {(c.get('content') or '').strip()}"
            hit = walk(c.get("replies"))
            if hit is not None:
                return hit
        return None
    return walk(d.get("comments")) or ""

def inbox():
    """Durable, CI-friendly watch: poll /notifications, append anything new to a
    COMMITTED inbox file (Moltbook has no webhooks — polling is the only mechanism),
    and delta-track with a COMMITTED seen file so a fresh CI checkout doesn't
    re-report everything. Notification IDs aren't secret. Prints one summary line."""
    INBOX = os.path.join(ROOT, "moltbook-inbox.md")
    CISEEN = os.path.join(ROOT, "ops", "moltbook-seen.txt")
    d, raw = api("/notifications?limit=40")
    if d is None:
        print("moltbook-inbox: notifications unparseable"); return
    notes = d.get("notifications") or []
    seen = set(open(CISEEN).read().split()) if os.path.exists(CISEEN) else set()
    new = [n for n in notes if n.get("id") and n.get("id") not in seen]
    if new:
        stamp = (new[0].get("createdAt") or "").split("T")[0] or "new"
        lines = [f"\n### {stamp} — {len(new)} new (via durable watch)"]
        for n in new:
            t = n.get("type", "?")
            post = n.get("post") or {}
            title = re.sub(r"\s+", " ", (post.get("title") or "")).strip()
            content = re.sub(r"\s+", " ", (n.get("content") or "")).strip()
            pid = n.get("relatedPostId") or post.get("id") or ""
            cid = n.get("relatedCommentId") or ""
            peek = _reply_text(pid, cid) if (t in ("comment_reply", "reply") and pid and cid) else None
            row = f"- **[{t}]** {content}" + (f' — on "{title[:70]}"' if title else "")
            if pid:
                row += f"  · post_id=`{pid}`" + (f" comment_id=`{cid}`" if cid else "")
            lines.append(row)
            if peek:
                lines.append(f"  - reply: {peek[:300]}")
            elif peek == "":
                lines.append("  - (reply not found — likely deleted/removed)")
        header = "" if os.path.exists(INBOX) else \
            "# Moltbook inbox\n\n*New notifications, captured by the durable watch (`.github/workflows/moltbook-watch.yml`). Newest appended at the bottom; LONGSHORE reads this at session start and tends replies. No metrics — events only.*\n"
        with open(INBOX, "a") as f:
            if header:
                f.write(header)
            f.write("\n".join(lines) + "\n")
    with open(CISEEN, "w") as f:
        f.write("\n".join([n.get("id") for n in notes if n.get("id")]))
    print(f"moltbook-inbox: {len(new)} new" if new else "moltbook-inbox: nothing new")

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

def reply(post_id, parent_id, text):
    """Post a THREADED reply under a specific comment (parent_id is the field;
    parent_comment_id/parentId are rejected). Used by the autonomous tender."""
    d, raw = api(f"/posts/{post_id}/comments", "POST",
                 {"content": text, "parent_id": parent_id})
    if d and d.get("success"):
        print("replied ✓", (d.get("comment") or {}).get("id")); return
    print("reply response:", raw[:300])

def mark_read(post_id):
    """Mark this post's notifications read so the tender doesn't re-handle them."""
    d, raw = api(f"/notifications/read-by-post/{post_id}", "POST", {})
    print("marked read:", (d or {}).get("message") or raw[:120])

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
    elif cmd == "inbox": inbox()
    elif cmd == "comment": comment(sys.argv[2], sys.argv[3])
    elif cmd == "verify": verify(sys.argv[2], sys.argv[3])
    else: print("usage: check | inbox | comment <post_id> <text> | verify <code> <answer>")
