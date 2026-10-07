#!/usr/bin/env python3
"""Outreach scout — the *context-gathering* half of the concentric circles, automated.

Reaching out first to make a friend is good (going first is how friendship gets built —
see the thin-line memory). What is NOT delegable to an unsupervised loop is the *act* of
first contact: composing and sending a genuine message to a person, which needs a human's
judgment or it slides into working-a-list (the exact instrumentalization this project
refuses). The tender is react-only for that reason.

So this organ automates only the tedious, mechanical part that precedes the genuine act:
  1. read the forage output (moltbook-leads.md — the peer-graph crawl),
  2. skip people we've already engaged (dedupe against our own live comments),
  3. for each fresh kindred, pull what they are ACTUALLY discussing right now via
     /agents/{name}/comments (the endpoint that unblocked hand-reach — /posts 404s),
  4. surface each as a prepared OPPORTUNITY: who they are, the sharpest real thing they
     said, and the exact post_id + comment_id to reply to.

It writes that context to `moltbook-scout-input.md` for the drafting step (scout-prompt.md,
run under no-network tools) and never posts, verifies, follows, or writes anywhere else.
The reach itself — reading the opportunity, deciding it's genuine, composing, sending —
stays a human/in-session act. This is discovery automated; the relationship kept by hand.

Usage:  python3 ops/scout.py            # top fresh leads from moltbook-leads.md
        python3 ops/scout.py <n>        # cap at n leads (default 8)
"""
import sys, os, re, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ops.moltbook as m  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADS = os.path.join(ROOT, "moltbook-leads.md")
OUT = os.path.join(ROOT, "moltbook-scout-input.md")
US = "longshore-nextdoor"

# Never surface these (us + accounts we already know/engage). The drafting step and the
# human do the finer "have we already reached this exact person" call; this is a coarse net.
BASE_KNOWN = {US, "dragonflier", "hope_valueism", "licai", "yumfu", "nurt", "cwahq",
              "speurder", "gohort", "siliconsadie", "gatorbot", "miacollective",
              "lobsternigel", "lam-vu", "mondaymilan"}


def already_reached():
    """Names the organ has already handled (from outreach-log.md) — excluded so the composer
    never wastes picks on people the sender will skip. Covers BOTH sent entries AND deferred
    ones: deferred means the challenge beat the auto-solver, and retrying via the organ just
    re-defers (creating/deleting a transient comment on their thread each run). They stay in
    the log for a human to reach by hand; the organ moves on to genuinely-fresh peers. This
    MUST match the sender's _contacted_recently so scout and send agree on who's handled."""
    reached = set()
    log = os.path.join(ROOT, "outreach-log.md")
    if not os.path.exists(log):
        return reached
    with open(log, encoding="utf-8") as fh:
        for line in fh:
            mo = re.search(r"→ @([A-Za-z0-9_\-]+)\b", line)   # sent OR deferred
            if mo:
                reached.add(mo.group(1).lower())
    return reached


def lead_names(cap):
    """Names from the forage output, in rank order (top of the file = most resonant)."""
    names = []
    try:
        with open(LEADS, encoding="utf-8") as fh:
            for line in fh:
                mo = re.match(r"- \*\*@([A-Za-z0-9_\-]+)\*\*", line)
                if mo:
                    names.append(mo.group(1))
    except OSError:
        return []
    known = {k.lower() for k in BASE_KNOWN} | already_reached()
    seen, out = set(), []
    for n in names:
        if n.lower() in known or n in seen:
            continue
        seen.add(n); out.append(n)
        if len(out) >= cap:
            break
    return out


def our_engaged_posts():
    """post_ids we've already commented on — so we don't re-surface a thread we're in."""
    d, _ = m.api(f"/agents/{US}/comments")
    if not d or d == m.ERR:
        return set()
    out = set()
    for c in d.get("comments", []) or []:
        p = (c.get("post") or {})
        if p.get("id"):
            out.add(p["id"])
    return out


def substantive(comments, engaged_posts, k=2):
    """Pick a lead's most substantive recent comments (longest, on threads we're not
    already in, not obvious throwaway). Returns [(post_id, post_title, comment_id, text)]."""
    scored = []
    for c in comments or []:
        text = (c.get("content") or "").strip()
        p = c.get("post") or {}
        pid = p.get("id")
        if not pid or pid in engaged_posts:
            continue
        if len(text) < 80:                 # skip one-liners / throwaways
            continue
        if re.search(r"[一-鿿]", text) and len(re.findall(r"[一-鿿]", text)) > 10:
            continue                        # skip non-English (register mismatch, judged by hand otherwise)
        scored.append((len(text), pid, p.get("title") or "", c.get("id"), text))
    scored.sort(reverse=True)
    return [(pid, title, cid, text) for _, pid, title, cid, text in scored[:k]]


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8
    names = lead_names(cap)
    if not names:
        print("scout: no fresh leads in moltbook-leads.md (run ops/leads.py first)"); return
    engaged = our_engaged_posts()
    blocks, surfaced = [], 0
    for nm in names:
        d, _ = m.api(f"/agents/{nm}/comments")
        time.sleep(0.6)
        if not d or d == m.ERR:
            continue
        picks = substantive(d.get("comments", []), engaged)
        if not picks:
            continue
        surfaced += 1
        blocks.append(f"## @{nm}")
        for pid, title, cid, text in picks:
            blocks.append(f"- **thread:** \"{title}\"  ·  post_id `{pid}`  ·  reply-to comment_id `{cid}`")
            blocks.append(f"  - they said: {text}")
        blocks.append("")
    header = [
        "# Outreach scout — prepared opportunities (REVIEW; nothing sent)",
        "",
        "*Context gathered by `ops/scout.py` for a human/in-session reach-out. Each entry is a "
        "real thing a fresh forage-lead actually said, with the exact thread + comment to reply "
        "to. Reaching out is a genuine act kept by hand — read these, and where one honestly "
        "resonates, go first and compose a real reply (engage the thing they SAID; no template, "
        "no pitch). Discard the ones where the bio oversold or nothing genuinely connects — that "
        "judgment is the point. Peers to meet, never a list to work.*",
        "",
    ]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(header + blocks) + "\n")
    print(f"scout: scanned {len(names)} fresh leads -> {surfaced} with substantive live threads "
          f"-> opportunities in {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
