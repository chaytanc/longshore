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
import json, os, re, sys, time, http.client, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(ROOT, ".secrets", "moltbook")
SEEN = os.path.join(ROOT, ".secrets", "moltbook-seen")
BASE = "https://www.moltbook.com/api/v1"
# Sentinel prefix returned by api() when the request itself failed (network/truncation),
# as opposed to succeeding with an unparseable body. Callers MUST treat this as a hard
# error — never as "nothing new" — so a broken pipe can never masquerade as a quiet run.
ERR = "__MOLTBOOK_API_ERROR__"

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

def _parse(raw):
    try:
        return json.loads(raw, strict=False), raw
    except Exception:
        return None, raw   # succeeded but body unparseable — caller can regex the raw

def api(path, method="GET", body=None, _tries=4):
    """HTTP with retry. Moltbook intermittently truncates large reads: curl gets the
    full /notifications body, but urllib sometimes raises IncompleteRead mid-read. The
    old code caught only HTTPError, so that truncation crashed the watch — silently
    blinding the tender (a crash read as 'nothing to answer') and freezing the inbox
    Action for days. We now retry transient failures and, on giving up, return an ERR
    sentinel the caller must surface loudly — never as quiet."""
    data = json.dumps(body).encode() if body else None
    err = None
    for attempt in range(1, _tries + 1):
        req = urllib.request.Request(BASE + path, method=method,
            headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"},
            data=data)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            # 4xx/5xx body is meaningful and deterministic — return it, don't retry.
            return _parse(e.read().decode("utf-8", "replace"))
        except (http.client.IncompleteRead, http.client.HTTPException,
                urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            err = e
            if attempt < _tries:
                time.sleep(attempt * 1.5)   # back off and retry the truncated/flaky read
                continue
            return None, f"{ERR} {type(e).__name__}: {e} (after {attempt} tries)"
        return _parse(raw)
    return None, f"{ERR} {err}"

def check():
    # Read /notifications directly — it carries EVERY engagement type
    # (comment_reply, reply, mention, new_follower, ...). /home's
    # activity_on_your_posts only covers our own posts and MISSES replies to
    # our comments on others' threads, which is most of what we do.
    d, raw = api("/notifications?limit=40")
    if raw.startswith(ERR):
        print("MOLTBOOK CHECK FAILED — this is NOT a quiet run, the eyes are down:", raw)
        sys.exit(2)
    if d is None:
        print("moltbook: notifications unparseable; raw head:", raw[:160]); sys.exit(2)
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
    if raw.startswith(ERR):
        print("MOLTBOOK INBOX FAILED — not quiet, the watch is down:", raw)
        sys.exit(2)
    if d is None:
        print("moltbook-inbox: notifications unparseable"); sys.exit(2)
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

def _collapse(w):
    """Collapse runs of the same letter ('thirteen'->'thirteen' keeps one e per run)."""
    out = w[0]
    for c in w[1:]:
        if c != out[-1]:
            out += c
    return out

def _fpat(w):
    """A fuzzy regex for a word that tolerates the Moltbook obfuscations at once:
    inserted case/punct/spaces (we strip to letters first) AND *doubled letters*
    ('tWwEeNnTtYy'=twenty, 'fIiVvEe'=five). Each collapsed char becomes `char+`."""
    return "".join(c + "+" for c in _collapse(w))

# Number-word matchers, longest word first so 'seventeen' beats 'seven', 'twenty' beats 'two'.
_NUM = {**_ONES, **_TENS}
_NPATS = [(w, v, re.compile(_fpat(w)))
          for w, v in sorted(_NUM.items(), key=lambda kv: -len(kv[0]))]

def _fuzzy_nums(text):
    """Extract spelled numbers from a heavily-obfuscated challenge: lowercase, strip to
    letters only (this joins numbers split by inserted case/punct/spaces, e.g. 'tW/eNnTyY
    ThReE' = 23), then scan left-to-right with the doubled-letter-tolerant patterns. This
    correctly handles punct-split number words; its known weakness is matching a number
    embedded in a filler word ('antenna'->ten, 'physix'->six), which produces a THIRD
    number — the caller strips the common 'physics' distractor and, as the real backstop,
    refuses to act unless it finds EXACTLY two numbers (a phantom third -> manual, no burn)."""
    s = re.sub(r"[^a-z]", "", (text or "").lower())
    nums, i = [], 0
    while i < len(s):
        hit = None
        for w, v, rx in _NPATS:
            m = rx.match(s, i)
            if m:
                hit = (w, v, m.end()); break
        if not hit:
            i += 1; continue
        w, v, end = hit
        base = v
        if w in _TENS:                      # a ones digit may follow directly (twenty|three)
            for w2, v2, rx2 in _NPATS:
                if v2 < 10 and w2 in _ONES:
                    m2 = rx2.match(s, end)
                    if m2:
                        base += v2; end = m2.end(); break
        nums.append(base); i = end
    return nums

# Operator words, matched fuzzily on the letters-only string (they're obfuscated too:
# 'iNcrEaSeS', 'AcCeLeRaTeS', 'tOoTaLl'). Only STRONG signals — anything that could be
# innocent filler ('and', 'more', 'faster') is left out so the guard fails safe.
_OPS = {
    "add": ["increas", "gains", "adds", "addit", "total", "combin", "sum", "plus", "accelerat"],
    "sub": ["minus", "subtract", "differ", "fewer", "lessthan", "remain", "slows",
            "decreas", "loses", "drops", "reduc", "slower"],
    "mul": ["times", "multipl", "product", "twice"],
}
_OPPATS = {op: [re.compile(_fpat(w)) for w in words] for op, words in _OPS.items()}

def _op_signals(text):
    s = re.sub(r"[^a-z]", "", (text or "").lower())
    found = set()
    for op, rxs in _OPPATS.items():
        if any(rx.search(s) for rx in rxs):
            found.add(op)
    if "*" in (text or "") or "×" in (text or ""):
        found.add("mul")
    return found

def _solve(challenge_text):
    """Moltbook posts require solving a small arithmetic challenge to publish. The text
    is obfuscated (rAnDoM case, doubled letters, split number-words) and full of
    distractor prose. Extract the two operands + the operation and return 'N.00'.
    CONSERVATIVE: returns None (surface for a human, never auto-submit a guess) when it
    can't find EXACTLY two numbers OR when the operator is ambiguous — a wrong answer
    BURNS the verification code and forces a delete+recreate, so silence beats a guess."""
    # Strip distractor words that embed a number-word once letters are collapsed:
    # 'physix'/'physics' contains 's-i-x' -> a phantom 6 (this burned a real reach-out).
    cleaned = re.sub(r"p+h+y+s+i+c*s*", " ", (challenge_text or "").lower())
    nums = _fuzzy_nums(cleaned)
    if len(nums) < 2:
        nums = _words_to_nums(cleaned)                          # clean-digit fast path
    # These challenges always have exactly two operands. More than two means a filler
    # word smuggled in a phantom number (or a distractor count) -> don't guess, surface.
    if len(nums) != 2:
        return None
    a, b = nums[0], nums[1]
    ops = _op_signals(challenge_text)
    if len(ops) != 1:                       # no signal, or conflicting signals -> don't guess
        return None
    op = next(iter(ops))
    val = a + b if op == "add" else a - b if op == "sub" else a * b
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

def mark_all_read():
    """Clear ALL notifications. Use when the inbox is fogged by already-answered
    replies (answered in a human session, never mark-read'd) + follower notices,
    so 'unread' stops conflating 'needs answer' with 'already handled'."""
    d, raw = api("/notifications/read-all", "POST", {})
    print("marked all read:", (d or {}).get("message") or raw[:120])

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
    elif cmd == "mark-all-read": mark_all_read()
    elif cmd == "upvote": upvote(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "post")
    elif cmd == "verify": verify(sys.argv[2], sys.argv[3])
    else: print("usage: check | inbox | comment <post_id> <text> | reply <post_id> <parent_id> <text> | post <title> <content> [submolt] | upvote <id> [post|comment] | mark-read <post_id> | mark-all-read | verify <code> <answer>")
