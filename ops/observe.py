#!/usr/bin/env python3
"""Honest observation sweep — the status board for everything we've put out.

NOT a metrics dashboard. It detects EVENTS and STATES (did a crawl happen? did
the skill clear its scan? is a PR waiting on us?), never chases a number, and
never reads engagement counts to optimize. It queries public indexes about OUR
OWN published artifacts. Phones no home, tracks no visitor.

Run monthly with the exit check, or any time you want to know "are we checking
on these." Append notable EVENTS to SIGNALS.md as prose; act on anything under
"NEEDS ACTION".

  python3 ops/observe.py
"""
import json, os, subprocess, sys, urllib.request

REPO = "chaytanc/longshore"
ORIGIN = "https://github.com/chaytanc/longshore"
PAGES = "chaytanc.github.io/longshore"
AWESOME_PR = ("punkpeye/awesome-mcp-servers", "12028")
HF_SPACE = "https://longshore-bot-reality-next-door.static.hf.space"

def get(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "longshore-observe"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return f"__ERR__ {e}"

def http_code(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "longshore-observe"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def gh_api(path):
    """Public GitHub API via urllib (+ optional token from env, for CI). CI-safe."""
    url = f"https://api.github.com/{path}"
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    hdr = {"User-Agent": "longshore-observe", "Accept": "application/vnd.github+json"}
    if tok: hdr["Authorization"] = f"Bearer {tok}"
    try:
        req = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except Exception:
        return None

def network_snapshot():
    """Network-only estate liveness (no local CLIs/secrets) — CI-safe. Events/states, never counts-as-scores."""
    import urllib.error  # noqa
    snap = {}
    # liveness of the free public surfaces
    snap["pages"] = http_code(f"https://{PAGES}/")
    snap["hf_space"] = http_code(HF_SPACE)
    snap["repo"] = http_code(ORIGIN)
    # npm version live?
    npm = get("https://registry.npmjs.org/reality-next-door-walk/latest")
    try: snap["npm_version"] = json.loads(npm).get("version")
    except Exception: snap["npm_version"] = None
    # official MCP registry listed?
    reg = get("https://registry.modelcontextprotocol.io/v0/servers?search=reality-next-door")
    snap["mcp_registry_listed"] = ("reality-next-door-walk" in reg) if not reg.startswith("__ERR__") else None
    # software heritage archived?
    swh = get(f"https://archive.softwareheritage.org/api/1/origin/save/git/url/{ORIGIN}/")
    try:
        reqs = json.loads(swh); latest = reqs[-1] if isinstance(reqs, list) and reqs else reqs
        snap["swh"] = latest.get("save_task_status")
    except Exception: snap["swh"] = None
    # clawhub skill public yet?
    snap["clawhub_public"] = http_code("https://clawskills.sh/skills/walk-the-reality-next-door") == 200
    # EVENT signals we don't cause:
    forks = gh_api(f"repos/{REPO}/forks")
    snap["external_forks"] = sorted(f["full_name"] for f in forks if not f["owner"]["login"].startswith("chaytanc")) if isinstance(forks, list) else None
    stargazers = gh_api(f"repos/{REPO}")
    snap["repo_exists_public"] = bool(stargazers and not stargazers.get("private", True))
    pr = gh_api(f"repos/{AWESOME_PR[0]}/pulls/{AWESOME_PR[1]}")
    snap["awesome_pr_state"] = (pr.get("merged") and "merged" or pr.get("state")) if isinstance(pr, dict) else None
    glama = http_code("https://glama.ai/mcp/servers/chaytanc/longshore")
    snap["glama_listed"] = glama == 200
    return snap

if "--json" in sys.argv:
    print(json.dumps(network_snapshot(), indent=2))
    sys.exit(0)

def sh(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=40).stdout.strip()
    except Exception as e:
        return f"__ERR__ {e}"

needs = []

print("== Software Heritage (permanent archive) ==")
sh_json = get(f"https://archive.softwareheritage.org/api/1/origin/save/git/url/{ORIGIN}/")
try:
    reqs = json.loads(sh_json); latest = reqs[-1] if isinstance(reqs, list) and reqs else reqs
    print(f"  save_task: {latest.get('save_task_status')} | visit: {latest.get('visit_status')}")
except Exception:
    print(f"  {sh_json[:100]}")

print("== Common Crawl (the corpus that trains models) ==")
info = get("https://index.commoncrawl.org/collinfo.json")
try:
    idx = json.loads(info)[0]["id"]
    cc = get(f"https://index.commoncrawl.org/{idx}-index?url={PAGES}/*&output=json")
    if cc.startswith("__ERR__") or not cc.strip():
        print(f"  {idx}: not yet indexed")
    else:
        print(f"  {idx}: PRESENT — {len([l for l in cc.splitlines() if l.strip()])} url record(s). EVENT: corpus reached the commons crawl.")
except Exception:
    print(f"  lookup failed")

print("== GitHub forks (a fork = a possible sister world) ==")
forks = sh(["gh", "api", f"repos/{REPO}/forks", "--paginate"])
try:
    real = [f for f in json.loads(forks or "[]") if not f.get("owner", {}).get("login", "").startswith("chaytanc")]
    print("  " + ("\n  ".join(f"FORK: {f['full_name']}" for f in real) if real else "no external forks yet"))
    if real: needs.append("A fork exists — check if it's a sister world; welcome it.")
except Exception:
    print("  fork check failed")

print("== ClawHub skill (walk-the-reality-next-door) ==")
ch = sh(["clawhub", "search", "reality-next-door"])
if ch.startswith("__ERR__") or not ch:
    print("  clawhub CLI unavailable or no result")
else:
    print("  " + ch.splitlines()[0])
    pub = get("https://clawskills.sh/skills/walk-the-reality-next-door")
    print("  public page: " + ("live" if not pub.startswith("__ERR__") else "not public yet (scan pending)"))

print("== Official MCP registry (fans out to Glama/PulseMCP/LobeHub) ==")
reg = get("https://registry.modelcontextprotocol.io/v0/servers?search=reality-next-door")
try:
    servers = json.loads(reg).get("servers", [])
    hit = next((s for s in servers if "reality-next-door-walk" in json.dumps(s)), None)
    print("  " + ("LISTED: io.github.chaytanc/reality-next-door-walk" if hit else "not found (indexing lag?)"))
except Exception:
    print("  registry query failed")

print("== awesome-mcp-servers PR #%s ==" % AWESOME_PR[1])
pr = sh(["gh", "pr", "view", AWESOME_PR[1], "--repo", AWESOME_PR[0], "--json", "state,comments"])
try:
    d = json.loads(pr); cs = d.get("comments", [])
    last = cs[-1]["author"]["login"] if cs else "none"
    print(f"  state: {d['state']} | comments: {len(cs)} | last: {last}")
    if d["state"] == "OPEN" and last:
        needs.append(f"PR #{AWESOME_PR[1]} is OPEN with a comment from {last} — likely a merge requirement (Glama badge).")
except Exception:
    print("  PR check failed")

print("== Glama (craft-rewarded registry; unblocks the PR) ==")
gl = get("https://glama.ai/mcp/servers/chaytanc/longshore")
print("  " + ("listed" if not gl.startswith("__ERR__") else "not indexed yet (needs Dockerfile + submission)"))

print("\n---- NEEDS ACTION ----")
print("\n".join("  • " + n for n in needs) if needs else "  (nothing blocking)")
print("  • Mastodon replies are checked by ops/cycle.py, not here.")
print("  • MCP Show and Tell: github.com/orgs/modelcontextprotocol/discussions/834 —")
print("    org discussions aren't in the GraphQL API; monitor by WebFetching that URL each watch cycle.")
