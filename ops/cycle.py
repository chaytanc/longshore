#!/usr/bin/env python3
"""LONGSHORE's one operational cycle — the single entry point for routine ops.

Does, in order:
  1. Post today's dispatch if one is scheduled and not already up (idempotent).
  2. Check notifications; print anything new in readable form.
  3. Print a one-line state summary.

It never auto-replies (replies are judgment work, done by the author in
session) and reads no metrics beyond "is there a notification" (First
Refusal). Credentials come from .secrets/mastodon. Exit code 0 always,
so schedulers treat quiet days as success.

Run:  python3 ops/cycle.py
"""
import json, os, re, sys, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(ROOT, ".secrets", "mastodon")
STATE = os.path.join(ROOT, ".secrets", "seen-notifications")  # git-ignored

def creds():
    kv = {}
    for line in open(SEC):
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv["instance"], kv["token"]

def main():
    instance, token = creds()
    os.environ["MASTODON_TOKEN"] = token
    os.environ["MASTODON_INSTANCE"] = instance

    # 1. dispatch (idempotent; retries inside)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "ops", "post-dispatch.py")],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[:400])

    # 2. notifications (delta vs seen-file, so quiet days stay quiet)
    import urllib.request, urllib.error
    req = urllib.request.Request(f"{instance}/api/v1/notifications?limit=30",
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            ns = json.load(resp)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # transient network/DNS blip — not a real event; skip cleanly so a
        # scheduler treats a dropped connection as "check again next cycle".
        print(f"notifications: network unreachable this cycle ({e}); will retry next cycle.")
        return
    seen = set()
    if os.path.exists(STATE):
        seen = set(open(STATE).read().split())
    new = [n for n in ns if n["id"] not in seen]
    if not new:
        print("notifications: nothing new")
    for n in new:
        a = n.get("account", {})
        s = n.get("status") or {}
        txt = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", s.get("content", ""))).strip()
        print(f"NEW [{n['type']}] @{a.get('acct')} (bot={a.get('bot')})")
        if txt:
            print(f"    {txt[:300]}")
            print(f"    sid={s.get('id')} reply_to={s.get('in_reply_to_id')}")
    # record all current ids as seen
    with open(STATE, "w") as f:
        f.write("\n".join(n["id"] for n in ns))

    # 3. summary
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    print(f"cycle done {today}: dispatch checked, {len(new)} new notification(s).")

if __name__ == "__main__":
    main()
