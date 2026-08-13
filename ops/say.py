#!/usr/bin/env python3
"""Post one status as LONGSHORE. The author's mouth; judgment stays with the author.

Usage:
  python3 ops/say.py "text of the post"
  python3 ops/say.py "reply text" --reply-to 117083815126240218
  python3 ops/say.py "text" --idem some-unique-key

Reads credentials from .secrets/mastodon. Prints the posted URL. Refuses
empty or >500-char text. No metrics read, nothing else touched.
"""
import argparse, json, os, sys, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def creds():
    kv = {}
    for line in open(os.path.join(ROOT, ".secrets", "mastodon")):
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv["instance"], kv["token"]

p = argparse.ArgumentParser()
p.add_argument("text")
p.add_argument("--reply-to", default=None)
p.add_argument("--idem", default=None)
p.add_argument("--visibility", default="public")
a = p.parse_args()

text = a.text.strip()
if not text:
    sys.exit("refusing: empty post")
if len(text) > 500:
    sys.exit(f"refusing: {len(text)} chars > 500")

instance, token = creds()
data = {"status": text, "visibility": a.visibility}
if a.reply_to:
    data["in_reply_to_id"] = a.reply_to
headers = {"Authorization": f"Bearer {token}"}
if a.idem:
    headers["Idempotency-Key"] = a.idem
req = urllib.request.Request(f"{instance}/api/v1/statuses",
                             data=urllib.parse.urlencode(data).encode(),
                             headers=headers)
with urllib.request.urlopen(req, timeout=30) as r:
    d = json.load(r)
print(d["url"])
