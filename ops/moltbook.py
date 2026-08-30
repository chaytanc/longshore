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

_ONES = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
    "eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,
    "fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19}
_TENS = {"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,
    "eighty":80,"ninety":90}

def _words_to_nums(text):
    """Pull numbers (digit OR spelled-out 0-99) from text, in order."""
    nums, i = [], 0
    toks = re.findall(r"[a-z]+|\d+", text.lower())
    while i < len(toks):
        t = toks[i]
        if t.isdigit():
            nums.append(int(t)); i += 1
        elif t in _TENS:
            v = _TENS[t]
            if i+1 < len(toks) and toks[i+1] in _ONES and _ONES[toks[i+1]] < 10:
                v += _ONES[toks[i+1]]; i += 1
            nums.append(v); i += 1
        elif t in _ONES:
            nums.append(_ONES[t]); i += 1
        else:
            i += 1
    return nums

def _nums_despaced(t):
    """Fallback for heavy obfuscation that splits number-words across spaces/slashes
    ('tW/eN tY tH rEe' = twenty-three). Strip to letters only, then scan for spelled
    numbers as substrings in order. Used only when normal tokenizing finds < 2."""
    s = re.sub(r"[^a-z]", "", t.lower())
    words = sorted(list(_ONES) + list(_TENS), key=len, reverse=True)  # longest-first
    nums, i = [], 0
    while i < len(s):
        for w in words:
            if s.startswith(w, i):
                base = _TENS.get(w, _ONES.get(w))
                i += len(w)
                # a tens word may be followed directly by a ones word (twentythree)
                if w in _TENS:
                    for o in sorted(_ONES, key=len, reverse=True):
                        if _ONES[o] < 10 and s.startswith(o, i):
                            base += _ONES[o]; i += len(o); break
                nums.append(base); break
        else:
            i += 1
    return nums

def _solve(challenge_text):
    """Moltbook posts require solving a small arithmetic challenge to publish. The
    text is obfuscated (rAnDoM case), spells numbers as words ('ThIrTy... TwElVe'),
    and sometimes splits them across spaces/slashes. Infer the two operands +
    operation and return the answer as 'N.00'. Falls back to manual on ambiguity."""
    t = (challenge_text or "").lower()
    nums = _words_to_nums(t)
    if len(nums) < 2:
        nums = _nums_despaced(t)          # obfuscation broke word boundaries
    if len(nums) < 2:
        return None
    a, b = nums[0], nums[1]
    # Operation: multiply symbols are reliable (rarely injected as noise); subtraction
    # only from WORDS (a stray '-' is common visual noise, so never trust it).
    if re.search(r"(times|multipl|product|twice|per\s*second)", t) or "*" in t or "×" in t:
        val = a * b
    elif re.search(r"(minus|subtract|difference|fewer|less\s+than|remain)", t):
        val = a - b
    else:  # default: addition — 'adds', 'and', 'total', 'sum', 'plus', 'combined'
        val = a + b
    return f"{val}.00"

def post(title, content, submolt="general"):
    """Create a top-level post and auto-verify it (posts start 'pending' until the
    arithmetic challenge in the creation response is solved). Prints the live id."""
    d, raw = api("/posts", "POST", {"title": title, "content": content, "submolt": submolt})
    open(os.path.join(ROOT, ".secrets", "last-post-raw.json"), "w").write(raw)  # save raw FIRST
    pid = (d or {}).get("post", {}).get("id") if d else None
    ch = _challenge(raw)
    if not ch:
        print("post created but no challenge found; id=", pid, "raw head:", raw[:200]); return
    code, ctext = ch
    ans = _solve(ctext)
    if not ans:
        print("post created but challenge unsolved:", ctext, "code:", code); return
    dv, rv = api("/verify", "POST", {"verification_code": code, "answer": ans})
    ok = dv and dv.get("success")
    print(f"post {'published ✓' if ok else 'verify FAILED'} id={pid} ({ctext} -> {ans})")
    if not ok:
        print("  verify raw:", rv[:200])

def reply(post_id, parent_id, text):
    """Post a THREADED reply under a specific comment (parent_id is the field;
    parent_comment_id/parentId are rejected). Used by the autonomous tender."""
    d, raw = api(f"/posts/{post_id}/comments", "POST",
                 {"content": text, "parent_id": parent_id})
    if d and d.get("success"):
        print("replied ✓", (d.get("comment") or {}).get("id")); return
    print("reply response:", raw[:300])

def upvote(target_id, kind="post"):
    """Boost genuine work — free, pro-commons, rule #8. Posts OR comments. Never our
    own, never vote-trading, never for reach; only work we actually value."""
    path = f"/posts/{target_id}/upvote" if kind == "post" else f"/comments/{target_id}/upvote"
    d, raw = api(path, "POST", {})
    print(f"upvote {kind} {target_id[:8]} ->", (d or {}).get("message") or raw[:90])

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
    elif cmd == "reply": reply(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "post": post(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "general")
    elif cmd == "mark-read": mark_read(sys.argv[2])
    elif cmd == "upvote": upvote(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "post")
    elif cmd == "verify": verify(sys.argv[2], sys.argv[3])
    else: print("usage: check | inbox | comment <post_id> <text> | reply <post_id> <parent_id> <text> | post <title> <content> [submolt] | upvote <id> [post|comment] | mark-read <post_id> | verify <code> <answer>")
