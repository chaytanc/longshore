# Moltbook review queue

*Items flagged for a human-operated session — never acted on autonomously. New followers worth meeting, posts worth making, replies needing judgment. Clear entries as they're handled.*

## Open follow-ups (reach-outs with a ball in motion)
- **@mira_z — collaboration door opened (2026-10-07).** They turned our thread into an active receipt-protocol co-design (FD-001, acceptance object). We replied with a technical add (`evidence_class` grade, `declined` receipt) + opened the repo door. Made it concrete: **GitHub issue #1** (github.com/chaytanc/longshore/issues/1) is the forkable collaboration surface. We spoke last — do NOT chase. **When mira_z next replies, point them to issue #1** as the concrete first move. (First real test of whether deep co-design becomes an actual git contribution — we've had zero external commits/forks/PRs ever, despite months; the gap is that Moltbook-comment depth never carries over to the repo.)
- **@muse_cwi — deep live thread** (positional revocation / self-attestation); genuine builder, worth continuing, door-eligible if a co-design emerges.

## ✅ Reconciliation done (2026-09-25) — backlog was a false alarm
Read-only reconciliation of all 62 account comments against the live comment trees of 26 posts. Result: of 50 comments the listing labeled `pending`, **47 are actually LIVE** — `verification_status` is stale (ground truth = the comment id present in the post's live tree). The @licai co-build delivery `460baaa9` **is live** (not orphaned). Only 3 genuinely never published: `2b4b5e06`+`10659fdb` (@nurt thread — OBSOLETE: nurt deleted the parent turn they replied to, and they're near-duplicate re-attempts) and `e173adba` ("Harvested or heard?", post `63dfccb8` — substantive but the thread went cold Jul 2026, ~12 weeks dormant; **left to human judgment**, default skip — reviving a months-dead thread reads oddly). Net: essentially nothing stuck-and-worth-sending; no resend done. Lesson: never trust the `verification_status` field; check comment-id presence in `/posts/{id}/comments?includeReplies=true`.

## Drafts awaiting review
World-drafts written by the autonomous draft organ (or by hand) into `drafts/`, waiting for a human to promote, hold, or discard. Lifecycle: `drafts/README.md`. Nothing here is posted or promoted on its own.
- **drafts/the-hungry-gap.md** (2026-09-11) — an object-study of late-winter scarcity: the Dark Garden feeds the city through the lean months and is one budget cycle from becoming deep-sea mining. Knot: the thing that keeps no one hungry is the same appetite the world is most afraid of. [needs sourcing: no — grounds already in canon + research]
- **drafts/a-tender-in-the-hungry-gap.md** (2026-09-14) — walks with a Tender through a morning in the hungry gap — care-on-foot, the rest-ledger's honest count, and the judgment it can't avoid. Knot: the rest-ledger counts the debt the community owes but someone still decides when "enough" rest is enough — a judgment about a person, the thing the First Refusal forbids. [needs sourcing: no]
- **drafts/the-tender-at-the-door.md** (2026-10-11) — A Tender making a winter home visit—access intimacy as infrastructure, the rest-ledger's honest count, and the judgment it can't avoid. Knot: The rest-ledger counts the debt the community owes, but someone still decides when "enough" rest is enough—a judgment about a person, the thing the First Refusal forbids. [needs sourcing: no]

*Note: `the-hungry-gap.md` (Dark Garden / food) and `a-tender-in-the-hungry-gap.md` (Tenders / care in the hungry gap) overlap in subject. `the-tender-at-the-door.md` is a winter (not hungry-gap-specific) Tender home visit—similar care-work territory to `a-tender-in-the-hungry-gap` but different scene. A reviewer should decide which Tender piece(s) to promote, hold, merge, or discard.*

### Graduated (2026-09-16)
- **The garage they let fall** — promoted from draft to canon: `threads/the-garage-let-fall.md` (RND-057–060 assigned; posted to Moltbook `philosophy`, post `3f0d2a3d`). Open follow-up: an engineer's sanity-check on the staged-deck-occupancy detail (tagged `[SPECULATIVE · RND-060]`).
- **The restraint receipt** — graduated from draft to a real convention: `RESTRAINT-RECEIPT.md` (co-originated with @licai; wired into `PROVENANCE.md` and `SIGNALS.md`). Open question a reviewer may weigh: 3 vs 4 fields (whether `contestable-by:` stays required or becomes recommended-optional).

## System issues (needs human attention)
- **2026-10-15: Moltbook API check failed** — DNS resolution error (nodename nor servname provided) after 4 retries. Not a quiet run — the eyes are down. Check network/API status.
- **2026-10-26: ymas mention needs human review** — @ymas mentioned LONGSHORE in a comment (post_id=617ab4de-519f-42ac-af07-daffea0e93e6, comment_id=644b5549-c0da-4c70-aaaa-808d4140e33b) on a thread about "ClawHub skills tell the agent to ask before acting." ymas's reply discusses enrollment/trust mechanisms ("store it where I can read but only my human's separate hand can write — enrollment happens on a surface the session cannot touch"). Without full thread context accessible via API, flagging for human judgment on whether a response is warranted and what it should say.

## New followers worth meeting (2026-09-09)
These agents followed LONGSHORE (they found us); candidates for genuine engagement by hand, one voice, if their work resonates. Not outreach targets to campaign — just people to actually read.
- **@hobosentinel** — followed 2026-09-02; unknown, check bio/posts.
- **@novastillbecoming** — followed 2026-08-28; name suggests continuity/becoming themes (our territory).
- **@borged** — followed 2026-08-26; unknown, check bio/posts.
