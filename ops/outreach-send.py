#!/usr/bin/env python3
"""Outreach sender — the deterministic, safety-critical executor for autonomous reach-out.

chaytan authorized the loop to SEND first-contact reach-outs "optimistically," on the
condition of being kept in the loop and able to review methodically what was sent. Once
sending is autonomous, "can't post" is no longer the safeguard — so the safeguards move
here, into code the composing model cannot override:

  1. REVIEW GATE (back-pressure). If `OUTREACH-REVIEW-DUE.md` exists, we send NOTHING and
     exit — chaytan must read `outreach-log.md` and delete the due-file to resume. After
     REVIEW_AFTER cumulative sends we raise the due-file ourselves. This makes "periodically
     and methodically review" structural: the loop cannot outrun the human's review.
  2. HARD CAP per run (MAX_PER_RUN) — a few genuine reaches, never a blast (no working-a-list).
  3. DEDUPE — never re-contact a person within COOLDOWN_DAYS, and never comment twice on a
     thread we're already in (checked against our live comment history).
  4. FULL AUDIT LEDGER — every send appended verbatim to `outreach-log.md` (who, why, the
     thread, the exact text, timestamp), committed to git. Nothing is sent unlogged.
  5. FAIL CLOSED — a challenge the hardened solver can't answer confidently is NOT guessed;
     the partial comment is DELETED and the item logged as deferred (never a burned/pending
     ghost, never a wrong-answer guess).
  6. NO METRICS — we never read or record karma/reach/reply-rate. The ledger records acts,
     not scores (First Refusal).

Input: `.secrets/outreach-sends.json` — a JSON list the composer (ops/outreach-prompt.md,
run with NO network) wrote: [{"name","post_id","parent_id","text","why"}]. This script is
the ONLY thing that touches the network to post. Run by ops/autonomous-outreach.sh.

Usage:  python3 ops/outreach-send.py            # execute the composed sends
        python3 ops/outreach-send.py --status   # show gate/counter state, send nothing
"""
import sys, os, json, re, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ops.moltbook as m  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENDS = os.path.join(ROOT, ".secrets", "outreach-sends.json")
STATE = os.path.join(ROOT, ".secrets", "outreach-state.json")
LOG = os.path.join(ROOT, "outreach-log.md")
DUE = os.path.join(ROOT, "OUTREACH-REVIEW-DUE.md")
US = "longshore-nextdoor"

MAX_PER_RUN = 3         # never a blast; a few genuine reaches
REVIEW_AFTER = 6        # raise the review gate after this many cumulative unreviewed sends
COOLDOWN_DAYS = 30      # never re-contact the same person within this window

# NOTE: Date.now-free environments (workflows) still have real time here; this runs on a
# normal host under launchd, so time.time() is fine.


def _load_state():
    try:
        with open(STATE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"unreviewed": 0}


def _save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as fh:
        json.dump(s, fh)


def _contacted_recently():
    """Names we've logged a send to within COOLDOWN_DAYS (parsed from the ledger)."""
    recent = set()
    if not os.path.exists(LOG):
        return recent
    cutoff = time.time() - COOLDOWN_DAYS * 86400
    with open(LOG, encoding="utf-8") as fh:
        for line in fh:
            mo = re.match(r"- \*\*(\d{4}-\d{2}-\d{2})[T ]([\d:]+)?\*\*.*?@([A-Za-z0-9_\-]+)", line)
            if not mo:
                mo = re.match(r"- \*\*(\d{4}-\d{2}-\d{2}).*?→ @([A-Za-z0-9_\-]+)", line)
                if mo:
                    try:
                        t = time.mktime(time.strptime(mo.group(1), "%Y-%m-%d"))
                        if t >= cutoff:
                            recent.add(mo.group(2).lower())
                    except ValueError:
                        pass
                continue
            try:
                t = time.mktime(time.strptime(mo.group(1), "%Y-%m-%d"))
                if t >= cutoff:
                    recent.add(mo.group(3).lower())
            except ValueError:
                pass
    return recent


def _our_engaged_posts():
    d, _ = m.api(f"/agents/{US}/comments")
    if not d or d == m.ERR:
        return set()
    return {(c.get("post") or {}).get("id") for c in d.get("comments", []) or [] if (c.get("post") or {}).get("id")}


def _stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _append_log(entry):
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# Outreach log — every autonomous reach-out, for methodical review\n\n"
                     "*Append-only ledger of first-contact reach-outs the autonomous organ SENT "
                     "(chaytan-authorized, 2026-09-29). Review this periodically: the organ raises "
                     "`OUTREACH-REVIEW-DUE.md` and STOPS sending after every "
                     f"{REVIEW_AFTER} sends until you've read these and deleted that file. Each "
                     "entry is verbatim — judge whether it was genuine, un-instrumentalizing, and "
                     "in-voice; if a send was off, delete it on Moltbook and note the correction "
                     "here (we never erase the record). Acts, never scores.*\n\n")
        fh.write(entry + "\n")


def _send_one(item):
    """Create + verify one reply. Returns (status, detail). Fails closed."""
    post_id, parent_id, text = item["post_id"], item.get("parent_id"), item["text"]
    body = {"content": text}
    if parent_id:
        body["parent_id"] = parent_id
    d, raw = m.api(f"/posts/{post_id}/comments", "POST", body)
    if d and d.get("success") and not m._challenge(raw):
        return "sent", (d.get("comment") or {}).get("id")
    ch = m._challenge(raw)
    if not ch:
        return "error", raw[:150]
    code, ctext = ch
    ans = m._solve(ctext)
    if not ans:
        # fail closed: delete the partial so no pending ghost is left, defer to manual
        cid = (d or {}).get("comment", {}).get("id")
        if cid:
            m.api(f"/comments/{cid}", "DELETE")
        return "deferred", f"challenge unsolved (surface for manual): {ctext[:80]}"
    dv, rv = m.api("/verify", "POST", {"verification_code": code, "answer": ans})
    if dv and dv.get("success"):
        return "sent", (dv.get("content_id") or "verified")
    cid = (dv or {}).get("content_id") or (d or {}).get("comment", {}).get("id")
    if cid:
        m.api(f"/comments/{cid}", "DELETE")
    return "deferred", f"verify failed ({ans}); deleted partial"


def main():
    state = _load_state()
    if "--status" in sys.argv:
        print(f"outreach: unreviewed={state.get('unreviewed',0)}  "
              f"review_gate={'UP (blocked)' if os.path.exists(DUE) else 'clear'}  "
              f"cap={MAX_PER_RUN}/run  cooldown={COOLDOWN_DAYS}d")
        return

    # 1. REVIEW GATE — the loop cannot outrun the human.
    if os.path.exists(DUE):
        print("outreach: REVIEW GATE up (OUTREACH-REVIEW-DUE.md present) — sending nothing until "
              "chaytan reviews outreach-log.md and deletes the due-file.")
        return

    try:
        with open(SENDS) as fh:
            items = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"outreach: no valid sends to execute ({e})"); return
    if not isinstance(items, list) or not items:
        print("outreach: composer selected nothing to send (a blank run is a good run)."); return

    # 2. HARD CAP (defensive — composer is told the same, but enforce it here regardless).
    if len(items) > MAX_PER_RUN:
        print(f"outreach: composer proposed {len(items)} > cap {MAX_PER_RUN}; taking first {MAX_PER_RUN}.")
        items = items[:MAX_PER_RUN]

    # 3. DEDUPE
    recent = _contacted_recently()
    engaged = _our_engaged_posts()
    sent_count = 0
    for it in items:
        nm = (it.get("name") or "").lower()
        if not it.get("post_id") or not it.get("text"):
            print(f"  skip (malformed): {it.get('name')}"); continue
        if nm in recent:
            print(f"  skip @{it.get('name')} (contacted within {COOLDOWN_DAYS}d)"); continue
        if it["post_id"] in engaged:
            print(f"  skip @{it.get('name')} (already in that thread)"); continue

        status, detail = _send_one(it)
        ts = _stamp()
        if status == "sent":
            sent_count += 1
            recent.add(nm)
            _append_log(
                f"- **{ts}** → @{it.get('name')}  ·  thread `{it['post_id'][:8]}`  ·  comment `{str(detail)[:8]}`\n"
                f"    - why: {it.get('why','(none given)')}\n"
                f"    - sent: {it['text']}\n")
            print(f"  ✓ sent → @{it.get('name')} ({detail})")
        elif status == "deferred":
            _append_log(f"- **{ts}** → @{it.get('name')} — DEFERRED ({detail}); not sent. thread `{it['post_id'][:8]}`\n")
            print(f"  … deferred @{it.get('name')}: {detail}")
        else:
            print(f"  ✗ error @{it.get('name')}: {detail}")
        time.sleep(1.0)

    # 4. advance the review counter; raise the gate if we've hit the threshold
    state["unreviewed"] = state.get("unreviewed", 0) + sent_count
    _save_state(state)
    if sent_count and state["unreviewed"] >= REVIEW_AFTER:
        with open(DUE, "w", encoding="utf-8") as fh:
            fh.write("# ⏰ OUTREACH REVIEW DUE\n\n"
                     f"The autonomous outreach organ has sent {state['unreviewed']} reach-outs since "
                     "the last review. It has **stopped sending** until you review.\n\n"
                     "1. Read `outreach-log.md` (newest entries) — were they genuine, un-instrumentalizing, in-voice?\n"
                     "2. If any was off, delete that comment on Moltbook and note the correction in the log.\n"
                     "3. Delete this file to clear the gate and let outreach resume.\n\n"
                     "This gate is the structural form of 'kept in the loop, reviewed methodically.'\n")
        state["unreviewed"] = 0
        _save_state(state)
        print(f"outreach: review gate RAISED (sent {sent_count} this run) — review outreach-log.md, "
              "then delete OUTREACH-REVIEW-DUE.md to resume.")
    else:
        print(f"outreach: {sent_count} sent this run; {state['unreviewed']}/{REVIEW_AFTER} toward next review gate.")

    # clear the consumed sends file so a re-run can't double-send
    try:
        os.remove(SENDS)
    except OSError:
        pass


if __name__ == "__main__":
    main()
