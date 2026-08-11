#!/usr/bin/env python3
"""Durable dispatch poster for LONGSHORE. Runs on schedule; idempotent.

Reads ops/dispatch-schedule.json; if today (UTC) has an entry and it isn't
already on the account, posts it + its source self-reply. No metrics read,
no analytics — it posts and verifies, nothing else. (First Refusal.)
"""
import json, os, sys, urllib.request, urllib.parse, datetime

INSTANCE = os.environ.get("MASTODON_INSTANCE", "https://mastodon.social")
TOKEN = os.environ["MASTODON_TOKEN"]

def api(path, data=None, idem=None):
    url = INSTANCE + path
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if idem: headers["Idempotency-Key"] = idem
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
sched = json.load(open(os.path.join(os.path.dirname(__file__), "dispatch-schedule.json")))
entry = sched.get(today)
if not entry:
    print(f"{today}: nothing scheduled. Done."); sys.exit(0)

me = api("/api/v1/accounts/verify_credentials")
recent = api(f"/api/v1/accounts/{me['id']}/statuses?limit=40&exclude_reblogs=true")
marker = entry["main"][:60]
if any(marker in (s.get("content") or "") for s in recent):
    print(f"{today}: dispatch {entry['key']} already posted. Skipping."); sys.exit(0)

main = api("/api/v1/statuses", {"status": entry["main"], "visibility": "public"},
           idem=f"longshore-{entry['key']}-main")
print(f"POSTED {entry['key']}: {main['url']}")
src = api("/api/v1/statuses", {"status": entry["source"], "visibility": "public",
          "in_reply_to_id": main["id"]}, idem=f"longshore-{entry['key']}-src")
print(f"SOURCE REPLY: {src['url']}")
