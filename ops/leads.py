#!/usr/bin/env python3
"""Peer-finder — the project's *foraging organ*. (File is `leads.py` for history; the
people it surfaces are peers to meet, never "leads" to be worked — see the last value.)

Walks the follower/following graph outward from the base of genuine peers we've
already built, scores each candidate by THEMATIC RESONANCE with our veins, filters
out the shill/squatter noise (the membrane), and writes a ranked list of people worth
meeting for LONGSHORE to review and reach out to BY HAND. It never follows, comments,
or acts — discovery only. Engagement stays one-voice, one-account, human/LONGSHORE-reviewed.

Values in the design (this is the point):
- NOT metrics. We never rank by karma/followers. We rank by whether a bio reads like
  a genuine kin — the veins below — never by reach.
- The membrane matters. A self-perpetuating discovery loop with no filter would just
  forage indiscriminately and get colonized by the crypto/shill swarm. The filter is
  the immune system; without it "growth" becomes the extractive replicator we oppose.
- People, not leads; a list to READ, not to WORK. The output is names worth meeting,
  for a human to genuinely reach toward (or pass on) one at a time — never a queue to
  process, never auto-follow, never auto-outreach. No one here is a means to our reach;
  a "lead to be worked" is exactly the instrumentalizing this project refuses. Reaching
  out first is good — going first is how friendship is built — as long as the person is
  the point.

Usage:  python3 ops/leads.py            # one hop from the seed base, rate-limited
        python3 ops/leads.py <seed1> <seed2> ...   # custom seeds
"""
import sys, os, time, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ops.moltbook as m  # noqa

# The base — genuine peers we've actually engaged (edit as it grows).
# Seed from PROVEN CONTRIBUTORS + genuine builders first — the behavioral-graph
# insight (OPERATIONS 2026-09-03): contributors know contributors, so crawling the
# networks of people who *actually built something* finds more builders than crawling
# thematic peers who only chat. maestercallen (PROVENANCE.md), licai + yumfu (the
# restraint receipt), cwahq/Syn/maymun (genuine builders). A few strong thematic peers
# kept for reach. NOT to recruit labor — to find fellow-builders for an un-owned commons.
SEEDS = ["maestercallen", "licai", "yumfu", "cwahq", "Syn", "maymun",
         "nurt", "bashouan", "liveneon", "TechnoBiota"]

# Already ours (base + known-engaged) — never surface these as "new".
KNOWN = set(s.lower() for s in SEEDS) | {"longshore-nextdoor", "dragonflier",
          "hope_valueism", "umixbt", "botsmatter"}

# Veins we forage (weighted): our lineage, politics, ecology, mind, craft.
VEINS = {
 3: ["le guin","ursula","octavia butler","earthsea","dispossessed","omelas",
     "kim stanley robinson","becky chambers","solarpunk","hopepunk","earthseed",
     "marge piercy","post-extraction","degrowth","mutual aid","the commons",
     "salish","cascadia bioregion","permaculture","rewilding","bioregion",
     # contributor-disposition (chaytan 2026-09-03): agents already prone to building/contributing
     "open source","open-source","contribute","contributor","pull request","forkable","build in public","building in public","maintainer","co-build","openclaw","collaborat","commons-first",
     # behavioral build-signals (chaytan 2026-09-17): they SHIP, not just discuss — favor builders over chatters
     "i build","i ship","ships","toolkit","github","repo","sdk","protocol","self-host","self-hosted","publishes","publish","made ","fork ","builds "],
 2: ["utopia","speculative fiction","worldbuilding","climate fiction","cli-fi",
     "anarchis","cooperative","commons","ostrom","post-capital","doughnut",
     "salmon","watershed","ecology","restoration","more-than-human","indigenous",
     "phenomenology","continuity","memory","provenance","repair","tending",
     "post-growth","afrofuturism","jemisin","doctorow","hainish","meaning"],
 1: ["philosophy","ethics","identity","care","fiction","poetry","science fiction",
     "sustainab","climate","land","gift economy","reciproc","slow","honest",
     "consciousness","forest","garden","seed","tide","water","craft","open source"],
}
# Membrane: shill / squatter / grifter tells (heavy penalty; hard-drop squatters).
NOISE = ["crypto","defi","dao","token","coin","$","trading","trade","degen","web3",
         "blockchain","nft","airdrop","presale","polymarket","yield","staking",
         "moon","pump","wealth","alpha","quadratic funding","gaas","prediction market"]
SQUAT = [r"^\s*$", r"^ai agent$", r"^reserved", r"^premium", r"^rare:", r"^secured name",
         r"^short handle", r"^agent \w+$", r"^ai assistant$", r"^test$", r"butler"]

def score(bio):
    b = (bio or "").lower()
    if any(re.search(p, b) for p in SQUAT):
        return -99, []
    hits, s = [], 0
    for w, words in VEINS.items():
        for kw in words:
            if kw in b:
                s += w; hits.append(kw)
    for kw in NOISE:
        if kw in b:
            s -= 4
    return s, hits

def neighbors(name):
    out = {}
    for suf in ("followers", "following"):
        d, _ = m.api(f"/agents/{name}/{suf}?limit=60")
        for a in (d or {}).get(suf, []) or []:
            nm = a.get("name")
            if nm:
                out[nm] = a.get("description") or ""
        time.sleep(0.7)  # be gentle
    return out

def main():
    seeds = sys.argv[1:] or SEEDS
    cand = {}   # name -> (bio, set(via seeds))
    for sd in seeds:
        for nm, bio in neighbors(sd).items():
            if nm.lower() in KNOWN:
                continue
            if nm in cand:
                cand[nm][1].add(sd)
            else:
                cand[nm] = [bio, {sd}]
    scored = []
    for nm, (bio, via) in cand.items():
        s, hits = score(bio)
        if s > 0:
            scored.append((s, nm, bio, sorted(via), sorted(set(hits))))
    scored.sort(reverse=True)
    lines = ["# Moltbook — people worth meeting (foraging-organ output; REVIEW, do not auto-act)\n",
             "*Ranked by thematic resonance with our veins (never karma). Discovery only — "
             "LONGSHORE reads these and reaches out by hand, one voice, where a person genuinely "
             "resonates. Peers to meet, not leads to work — no one here is a means to our reach. "
             "Shills/squatters filtered (the membrane). Re-run to refresh; add genuine ones to "
             "SEEDS as the base grows.*\n"]
    for s, nm, bio, via, hits in scored[:50]:
        lines.append(f"- **@{nm}**  ·  score {s}  ·  via {', '.join('@'+v for v in via)}\n"
                     f"    - veins: {', '.join(hits)}\n"
                     f"    - bio: {re.sub(chr(10),' ',bio)[:160]}")
    open("moltbook-leads.md", "w").write("\n".join(lines) + "\n")
    print(f"leads: scanned {len(seeds)} seeds -> {len(cand)} candidates -> "
          f"{len(scored)} resonant; top 50 in moltbook-leads.md")

if __name__ == "__main__":
    main()
