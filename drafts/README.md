# drafts/ — the world's waiting room

*Unreviewed world-drafts land here. Nothing in this folder has been approved, and nothing here is ever posted or promoted on its own. This is a staging area between the autonomous **draft organ** and a human's judgment.*

## Where these come from

The draft organ (`ops/draft-prompt.md`, run headless by `ops/autonomous-draft.sh`) reads the canon and research and writes **one small, cited world-piece** here — or writes nothing, which is the common and correct result. It runs with no Bash, no network, and no Moltbook: it *cannot* post, and it can only build from sources already vetted in this repo. See `PRESENCES.md` for how it's wired and how to turn it on (it's off by default).

A human can also just write a draft here by hand. Same waiting room.

## The lifecycle (a human does this, in-session)

Each draft carries a `status: UNREVIEWED` header, a `grounds:` line (what it stands on), `the-knot:` (the tension it must leave open), and `needs-a-human-to-source:` (claims to verify before it goes anywhere). To handle one:

1. **Read it against the canon.** Does it contradict `CANON.md`? Does it resolve a tension it shouldn't (Rule Zero)? Is the voice plain and load-bearing, or is it brochure?
2. **Check the receipts.** Every real-world claim must trace to a real source. Resolve everything under `needs-a-human-to-source:` — the organ was forbidden from inventing sources, so it flagged them for you.
3. **Then one of:**
   - **Promote** — move it into `threads/`, refine it, assign real RND numbers in `PROVENANCE.md` (drafts carry only provisional `[TAG · draft]` markers so they can't collide), and commit. Now it's canon-adjacent world.
   - **Hold** — leave it here with a note if it's close but not ready.
   - **Discard** — delete it. Most drafts may not survive, and that's the filter working, not a loss.
4. **Clear its pointer** from the "Drafts awaiting review" section of `moltbook-review-queue.md`.

## The line

Promotion, refinement, and anything outward-facing (posting a dispatch to a venue) are **human, in-session** — same rule as the rest of the project. The organ keeps the world *moving*; a person keeps it *honest*. Keeping those two jobs separate is the whole design.
