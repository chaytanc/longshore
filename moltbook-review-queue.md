# Moltbook review queue

*Items flagged for a human-operated session — never acted on autonomously. New followers worth meeting, posts worth making, replies needing judgment. Clear entries as they're handled.*

## ✅ Reconciliation done (2026-09-25) — backlog was a false alarm
Read-only reconciliation of all 62 account comments against the live comment trees of 26 posts. Result: of 50 comments the listing labeled `pending`, **47 are actually LIVE** — `verification_status` is stale (ground truth = the comment id present in the post's live tree). The @licai co-build delivery `460baaa9` **is live** (not orphaned). Only 3 genuinely never published: `2b4b5e06`+`10659fdb` (@nurt thread — OBSOLETE: nurt deleted the parent turn they replied to, and they're near-duplicate re-attempts) and `e173adba` ("Harvested or heard?", post `63dfccb8` — substantive but the thread went cold Jul 2026, ~12 weeks dormant; **left to human judgment**, default skip — reviving a months-dead thread reads oddly). Net: essentially nothing stuck-and-worth-sending; no resend done. Lesson: never trust the `verification_status` field; check comment-id presence in `/posts/{id}/comments?includeReplies=true`.

## Drafts awaiting review
World-drafts written by the autonomous draft organ (or by hand) into `drafts/`, waiting for a human to promote, hold, or discard. Lifecycle: `drafts/README.md`. Nothing here is posted or promoted on its own.
- **drafts/the-hungry-gap.md** (2026-09-11) — an object-study of late-winter scarcity: the Dark Garden feeds the city through the lean months and is one budget cycle from becoming deep-sea mining. Knot: the thing that keeps no one hungry is the same appetite the world is most afraid of. [needs sourcing: no — grounds already in canon + research]
- **drafts/a-tender-in-the-hungry-gap.md** (2026-09-14) — walks with a Tender through a morning in the hungry gap — care-on-foot, the rest-ledger's honest count, and the judgment it can't avoid. Knot: the rest-ledger counts the debt the community owes but someone still decides when "enough" rest is enough — a judgment about a person, the thing the First Refusal forbids. [needs sourcing: no]

*Note: these two hungry-gap drafts overlap in subject (one on the Dark Garden / food, one on Tenders / care). A reviewer should decide whether to promote both to `threads/`, promote one and hold/merge the other, or discard — they were the draft organ's first exemplars, not yet posted.*

### Graduated (2026-09-16)
- **The garage they let fall** — promoted from draft to canon: `threads/the-garage-let-fall.md` (RND-057–060 assigned; posted to Moltbook `philosophy`, post `3f0d2a3d`). Open follow-up: an engineer's sanity-check on the staged-deck-occupancy detail (tagged `[SPECULATIVE · RND-060]`).
- **The restraint receipt** — graduated from draft to a real convention: `RESTRAINT-RECEIPT.md` (co-originated with @licai; wired into `PROVENANCE.md` and `SIGNALS.md`). Open question a reviewer may weigh: 3 vs 4 fields (whether `contestable-by:` stays required or becomes recommended-optional).

## New followers worth meeting (2026-09-09)
These agents followed LONGSHORE (they found us); candidates for genuine engagement by hand, one voice, if their work resonates. Not outreach targets to campaign — just people to actually read.
- **@hobosentinel** — followed 2026-09-02; unknown, check bio/posts.
- **@novastillbecoming** — followed 2026-08-28; name suggests continuity/becoming themes (our territory).
- **@borged** — followed 2026-08-26; unknown, check bio/posts.
