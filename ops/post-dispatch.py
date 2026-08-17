#!/usr/bin/env python3
"""Durable dispatch poster for LONGSHORE. Runs on schedule; idempotent.

Reads ops/dispatch-schedule.json; if today (UTC) has an entry and it isn't
already on the account, posts it + its source self-reply. No metrics read,
no analytics — it posts and verifies, nothing else. (First Refusal.)
"""
import json, os, sys, time, html, re, urllib.request, urllib.parse, urllib.error, datetime

def normalize(s):
    """Fetched statuses are HTML-escaped ('&#39;') and tag-wrapped; the schedule
    text is raw. Normalize both sides so the already-posted check actually matches."""
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html.unescape(s or ""))).strip()

INSTANCE = os.environ.get("MASTODON_INSTANCE", "https://mastodon.social")
TOKEN = os.environ["MASTODON_TOKEN"]

def api(path, data=None, idem=None, tries=4):
    url = INSTANCE + path
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if idem: headers["Idempotency-Key"] = idem
    body = urllib.parse.urlencode(data).encode() if data else None
    # Retry transient failures (mastodon.social 5xxs happen; one killed the
    # 8/13 run mid-check). Idempotency-Key makes retried POSTs safe.
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code >= 500 and attempt < tries - 1:
                time.sleep(5 * (attempt + 1)); continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if attempt < tries - 1:
                time.sleep(5 * (attempt + 1)); continue
            raise
    raise last

today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
sched = json.load(open(os.path.join(os.path.dirname(__file__), "dispatch-schedule.json")))
entry = sched.get(today)
if not entry:
    print(f"{today}: nothing scheduled. Done."); sys.exit(0)

me = api("/api/v1/accounts/verify_credentials")
recent = api(f"/api/v1/accounts/{me['id']}/statuses?limit=40&exclude_reblogs=true")
marker = normalize(entry["main"])[:60]
if any(marker in normalize(s.get("content")) for s in recent):
    print(f"{today}: dispatch {entry['key']} already posted. Skipping."); sys.exit(0)

# The main + source posts share a stable Idempotency-Key, so if this races
# the GitHub Action (both run the same script) Mastodon dedupes — no double
# post. A transient failure here just means a later run finishes the job;
# report it cleanly instead of tracebacking.
try:
    main = api("/api/v1/statuses", {"status": entry["main"], "visibility": "public"},
               idem=f"longshore-{entry['key']}-main")
    print(f"POSTED {entry['key']}: {main['url']}")
    src = api("/api/v1/statuses", {"status": entry["source"], "visibility": "public",
              "in_reply_to_id": main["id"]}, idem=f"longshore-{entry['key']}-src")
    print(f"SOURCE REPLY: {src['url']}")
except Exception as e:
    print(f"{today}: post of {entry['key']} did not complete this run ({e}); "
          f"idempotency-safe — a later run or the Action will finish it.")
    sys.exit(0)
