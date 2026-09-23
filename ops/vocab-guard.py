#!/usr/bin/env python3
"""Vocab-guard — the immune system against influence-op vocabulary rot.

The project deliberately purged marketing / influence-op vocabulary once (see
OPERATIONS 2026-08-something: "beachhead," "seed(ing)," "work the leads,"
"primed audience," "converts"). Prose and memory can't hold that line — every
new session (including the autonomous tender writing journal entries) can quietly
reintroduce the words. This guard makes the ban *checkable* instead of promised:
it fails a commit when the rot grows back. That is the whole project's method
applied to itself — a value held by structure, not by good intentions
(see the memory `longshore-the-thin-line`).

Two tiers, precision-first (a noisy guard gets ignored, which is the same failure
in reverse):

  HARD  — marketing collocations that are essentially always slop when we write
          them about our own work ("primed audience", "conversion rate", "work
          the leads"). Checked in EVERY tracked prose file.

  SOFT  — bare words that are usually innocent English (a D&D "campaign", a
          diffusion-theory "audience", "lead with a snippet") but are genuine
          rot when they shape live behaviour. Checked ONLY in the small set of
          forward-facing operational files below.

Deliberate uses — the confessions that NAME the influence-op machinery on
purpose ("A campaign that still calls its readers 'converts'…"), the refusals
("no one is a lead to be worked"), and innocent verbs ("lead with a story") —
are blessed by ANCHORS (a short unique phrase from the line) or by an inline
`vocab-ok` marker. Blessing the whole confession is correct: if someone later
edits that line into real rot, the anchor stops matching and the guard trips.
Do NOT scrub the honest confessions — that would be a worse failure than the rot.

Usage:  python3 ops/vocab-guard.py            # scan tracked files; exit 2 on rot
        python3 ops/vocab-guard.py --list      # show the banned lists and exit
"""
import sys, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- HARD: marketing/influence-op collocations. Checked everywhere. -----------
# (regex, why, suggested replacement)
# Only phrases that are NEVER legitimate here — they can't be a named-refusal
# (nobody writes "we don't run a conversion funnel"; the refusals are stated
# positively). Approving use == rot, everywhere, no exceptions.
HARD = [
    (r"\b(primed|target)\s+audience\b", "marketing framing of our own readers",
     "the people most likely to resonate"),
    (r"\boutreach\s+targets?\b", "people are not targets", "people to reach out to"),
    (r"\bwork(?:ing)?\s+the\s+leads?\b", "the influence-op tell, by name", "reach toward peers, one at a time"),
    (r"\bnurtur\w*\s+(?:the\s+)?leads?\b", "CRM vocabulary for people", "stay in touch with peers"),
    (r"\blead\s+(?:magnet|generation|gen|list)\b", "funnel vocabulary", "—"),
    (r"\bconversion\s+rate\b", "friendship has no conversion rate", "—"),
    (r"\b(sales|marketing|conversion)\s+funnel\b", "funnel = instrumentalized people", "—"),
]
# NOT guarded on purpose: "engagement bait", "growth-hack", "CTA / call to
# action", "A/B test", "sockpuppet", "astroturf", "dark pattern". The project's
# honest voice NAMES these as things it refuses ("no engagement bait", "killed
# the marketer CTA") — guarding them would flag the confessions, not the rot.
# Their approving use is real rot but rare and not regex-detectable; the SOFT
# words and the collocations above cover the actual regrowth vectors.

# --- SOFT: bare words. Checked ONLY in forward-facing operational files. -------
SOFT = [
    (r"\btargets?\b", "a person is not a target", "person / peer"),
    (r"\bleads?\b", "a person is not a lead", "peer to meet"),
    (r"\bconverts?\b|\bconversion\b", "readers are not conversions", "a turn / someone who turned"),
    (r"\bcampaign\b", "no coordinated push (the influence-op charge)", "reword per case"),
    (r"\bbeachhead\b", "borrowed from influence ops", "depth before breadth / first community"),
    (r"\bfunnel\b", "instrumentalized-people vocabulary", "—"),
]

# Files that shape live outward behaviour — SOFT words are treated as rot here.
FORWARD = {
    "agents/longshore.persona.md",
    "agents/longshore.replies.md",
    "agents/longshore.fediverse.md",
    "agents/corposant.md",
    "agents/neon-moss.persona.md",
    "ops/tend-prompt.md",
    "ops/draft-prompt.md",
    "ops/voice-review-prompt.md",
    "moltbook-review-queue.md",
    "README.md",
    "the-first-move.md",
    "STRATEGY.md",
    "LAUNCH.md",
}

# --- ANCHORS: bless deliberate confessions / refusals / innocent verbs. --------
# path -> list of short unique substrings; a matching line containing one is exempt.
# These are the honest uses. Editing the line into real rot breaks the anchor => trips.
ANCHORS = {
    "agents/longshore.persona.md": [
        "still calls its readers",           # the steelman confession
        "a \"conversion\")?",                # "no one is a lead" refusal (line 47)
        "friendship has no conversion rate", # refusal
        "no one — human or agent — is a lead to be worked",
        "whether they lead with a code snippet",  # innocent verb
    ],
    "agents/longshore.replies.md": [
        "peer to meet, never a lead to be worked",
        "agonism, not conversion",           # section heading
        "No campaign; let them reach",       # refusal
    ],
    "ops/tend-prompt.md": [
        "not running a campaign and must not behave like one",  # refusal
    ],
    "ops/voice-review-prompt.md": [
        "never let reach become the target",  # refusal
        "it lands better / converts more",    # naming what we KILL
    ],
    "moltbook-review-queue.md": [
        "Not outreach targets to campaign",   # refusal in prose
    ],
    "LAUNCH.md": [
        "once used words like \"beachhead\"",  # the confession about removing them
    ],
    "OPERATIONS.md": [
        "Took the borrowed marketing/influence-op words",  # dated journal: documents the removal
    ],
}

MARKER = "vocab-ok"  # inline escape hatch: any line containing this token is exempt.


def tracked_md():
    out = subprocess.check_output(["git", "-C", ROOT, "ls-files", "*.md"], text=True)
    return [p for p in out.splitlines() if p.strip()]


def blessed(relpath, line):
    if MARKER in line:
        return True
    for anc in ANCHORS.get(relpath, []):
        if anc in line:
            return True
    return False


def scan():
    hits = []
    for rel in tracked_md():
        path = os.path.join(ROOT, rel)
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError):
            continue
        rules = list(HARD)
        if rel in FORWARD:
            rules = rules + [(rx, why, sug) for rx, why, sug in SOFT]
        for i, line in enumerate(lines, 1):
            if blessed(rel, line):
                continue
            for rx, why, sug in rules:
                m = re.search(rx, line, re.IGNORECASE)
                if m:
                    hits.append((rel, i, m.group(0), why, sug, line.rstrip()))
    return hits


def main():
    if "--list" in sys.argv:
        print("HARD (checked everywhere):")
        for rx, why, sug in HARD:
            print(f"  {rx!r:40}  {why}  ->  {sug}")
        print("\nSOFT (checked only in forward-facing files):")
        for rx, why, sug in SOFT:
            print(f"  {rx!r:40}  {why}  ->  {sug}")
        print("\nForward-facing files:")
        for f in sorted(FORWARD):
            print(f"  {f}")
        return 0

    hits = scan()
    if not hits:
        print("vocab-guard: clean — no influence-op vocabulary rot found.")
        return 0

    print(f"vocab-guard: {len(hits)} possible rot(s) found "
          f"(bless a deliberate use with a `{MARKER}` marker or an ANCHORS entry):\n")
    for rel, ln, term, why, sug, text in hits:
        print(f"  {rel}:{ln}  “{term}” — {why}")
        print(f"      -> {sug}")
        snippet = text.strip()
        if len(snippet) > 140:
            snippet = snippet[:137] + "..."
        print(f"      {snippet}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
