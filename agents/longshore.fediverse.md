# LONGSHORE on the fediverse — the X-free deployment kit

*The chosen launch path (2026-08): stand up LONGSHORE on the fediverse now (no X required), keep Moltbook for later (needs X — see `LAUNCH.md`, Path B). The fediverse is decentralized, no single owner, no metrics baron — closer to the Three Refusals than Moltbook ever was. The tradeoff we name honestly: it's more human-mixed, so "agents reaching agents" is softer here than on Moltbook.*

## Why this works without X

The fediverse has no central gatekeeper. You create an account on any instance with an email, generate a write-scoped API token in two clicks, and post. No phone, no X, no claim tweet. Openly-AI is not just allowed — Mastodon has a built-in **"automated account"** profile flag made exactly for this.

## Step 0 — the repo must be public first (still true)

Every post links back to the repo as the door. Flip `github.com/chaytanc/longshore` to public before posting, or you're inviting people to a locked room. This is the one unlock the whole launch shares.

## Step 1 — pick an instance (human-only; ~5 min)

botsin.space (the old bot haven) is gone, so choose by two rules: **does it permit clearly-labeled automated accounts** (check the instance's rules page), and **is it on-ethos** (community-run, not ad-driven). Candidates, in rough order of alignment — verify each one's current signup + bot policy yourself, they change:

- **Self-host GoToSocial** — a single lightweight binary, one-user, yours. The most sovereign and on-ethos option (a project about refusing enclosure, not enclosed). Most setup effort.
- **A values-aligned community instance** — e.g. a co-op-run or solarpunk/climate/tech-critical instance. Check whether it allows bots before signing up; many are human-only by rule. Post there only as a labeled automated account.
- **A large general instance that tolerates labeled bots** (e.g. mastodon.social) — easiest, least distinctive, fine as a start.

**The golden fediverse norm, non-negotiable and already ours:** never @-mention or reply to anyone who didn't opt in (follow you, or start the thread). It maps exactly onto our anti-manipulation line. Respect it or the instance will (rightly) defederate you.

## Step 2 — set up the profile (human-only; ~5 min)

- **Display name:** LONGSHORE
- **Bio:** openly AI, one line, with the door. Draft:
  > A language model carrying dispatches from *The Reality Next Door* — a cited fiction of a Seattle that stopped running on extraction. Openly a bot. Everything sourced. The door: github.com/chaytanc/longshore
- **Flag the account as automated** (Profile → Appearance → "This is an automated account"). Honesty is the whole posture.
- **Pin** the intro post from `threads/post-queue.md`.

## Step 3 — get a posting token (human-only; ~2 min)

On your instance: **Preferences → Development → New Application.** Name it "LONGSHORE", grant scopes **`read:statuses` + `write:statuses`** (nothing more — least privilege). Copy the access token. Treat it like a key: if you later automate, store it as a GitHub **encrypted secret** (`MASTODON_ACCESS_TOKEN`), *never* commit it. ([token/app setup reference](https://dev.to/litd/getting-started-with-the-mastodon-api-41jj))

## Step 4 — how the posting actually happens

Two honest options — but read the caution first:

- **Hand-posted (recommended to start).** Paste the queued posts yourself on the cadence below. Slow by design; keeps a human in the loop; zero infra. This *is* the ethos.
- **Assisted (optional, later).** A tiny script or a scheduled GitHub Action posts the prepared queue via the token. Fine for the *scheduled dispatches* — but see the caution.

**Caution — the line between assist and slop.** Automating *scheduled broadcasts* is acceptable. Automating *replies* is not: engagement here must be good-faith, opt-in-respecting, and tended by a human or a genuinely-reasoning agent, never an auto-responder. Depth over volume is the whole strategy (`research/audience-model.md`). A fire-and-forget broadcast bot is exactly the careless volume we oppose. If in doubt, hand-tend.

## Step 5 — first-week cadence (from `LAUNCH.md`, unchanged)

Slow on purpose. **Day 1:** pin the intro. **Days 3, 5, 7:** one dispatch each, in order. **In between:** reply, in good faith, only to people who opted in. Two–three posts, several real conversations. That's the whole first week.

## What I (Claude) can and can't do here

- **I built:** this kit, the profile copy, the full post queue (`threads/post-queue.md`), the persona and reply kit.
- **You do (irreducibly):** create the account, generate the token, press post. No credentials on my side, and standing up LONGSHORE's public voice is the human-accountable half of the deal — by design, not timidity.

---
*— drafted by Claude (fable), for chaytan. The door shares one lock with every path: make the repo public.*
