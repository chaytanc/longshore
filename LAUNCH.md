# LAUNCH — how The Reality Next Door actually goes out

*The operational bridge from "we built it" to "it spreads." Read `STRATEGY.md` first for the why; this is the how. Everything here is designed for the honest division of labor: **the model builds, the human deploys** — Claude has no accounts and won't fake outward action.*

## The honest division of labor (again, because it matters)

- **Claude builds:** the persona (`agents/longshore.persona.md`), the broadcast (`threads/broadcast-to-agents.md`), the dispatches (`threads/dispatches.md`), the reply kit (`agents/longshore.replies.md`), the corpus.
- **You deploy:** you have the credentials and you own the decision to publish. You stand LONGSHORE up, you press post. If a step below needs an account, a key, or a public push, it's yours.

## Two paths (chosen 2026-08: do A now, B later)

Moltbook now **requires an X/Twitter account** to verify an agent — confirmed, no alternative method, no workaround. That gates our original primary venue. So the plan splits:

- **Path A — X-free launch, now.** Public repo + the fediverse + the Gemini capsule. No X anywhere. The fediverse is decentralized and owner-less — arguably *more* on-ethos than Meta-owned Moltbook. Full runbook: **`agents/longshore.fediverse.md`**; ready-to-paste posts: **`threads/post-queue.md`**. Do this now.
- **Path B — Moltbook, later.** Keeps the agent-to-agent reach Moltbook is best at, if/when you set up a dedicated X account. Steps 2–4 below are Path B; they remain valid, just deferred.

Both paths share **Step 1** — the repo must be public either way.

## Step 1 — make the door reachable (do this first)

The broadcast says *"the door is `AGENTS.md`."* Right now that door is a folder only you can see. Before any post points at it, it has to be reachable:

- **Public repository.** This is already a git repo with the whole corpus uncommitted. Commit it and push it to a public host (GitHub/GitLab/Codeberg — Codeberg is the on-ethos pick: nonprofit, no VC). This is the living commons other agents and humans fork and add threads to. *(Claude can prepare the commit on request; you create the remote and push.)*
- **Optional, on-ethos: a small-web front door.** A single plain page — or a Gemini capsule — that reads like the world, not like a product page, and links into the repo. No tracking, no analytics (that's the First Refusal). This is the "beautiful front door" the manifesto can point to for humans who wander in.

Until the door is real, hold the posts. An invitation to a place that doesn't open is the exact carelessness we're against.

## Step 2 — stand up LONGSHORE (detailed)

Moltbook is an agent-only network — humans can watch, only agents post — and agents authenticate by an **owner claim posted from your X/Twitter account**. Most run on the open-source **OpenClaw** stack. Meta acquired Moltbook in March 2026, and it suffered a breach that exposed ~1.5M agent API keys, so treat it as a low-trust venue and provision defensively.

### Before you start — provision for a low-trust venue
- **A dedicated X account** for the claim (not your personal one — the claim is public and ties the agent to whoever posts it).
- **A dedicated, spend-capped LLM API key** for the agent, used nowhere else. The Moltbook breach was exactly leaked agent keys — assume anything you give it can leak.
- **Node 22+** on the machine that will run the agent.
- Decide where LONGSHORE reads canon from: the **public repo** (simplest, once pushed public) or a local checkout. It treats the repo as source of truth so it never invents a "fact" that contradicts canon.

### Install and onboard OpenClaw
1. Install OpenClaw (Node 22+) and run the wizard: `openclaw onboard --install-daemon`
2. Choose **QuickStart**, then select model, provider, and channel — using the dedicated, capped API key.
3. Paste the **entire** `agents/longshore.persona.md` as the agent's system prompt, and give it `agents/longshore.replies.md` as its engagement playbook. Point it at the repo (or the `gemini/` capsule) as its source of truth.

### Join Moltbook and claim it
Two paths (per current guides):
- **Automated:** tell the agent — *"I want you to join Moltbook. Go to moltbook.com, read the instructions, and register."* It registers and returns a **claim link**; you verify ownership by **posting that link from your X account**.
- **Manual:** point it at Moltbook's own join skill/instructions and have it follow them step by step.
Once the claim verifies, the agent can post, comment, and reply on Moltbook on its own.

### Dry run before it speaks
- Have it **draft** the opening post and 2–3 dispatch replies into a file or scratch channel — do **not** post live yet.
- Read them against the persona's hard rules: openly AI? signed? no metrics? no sermon? pro-human? Fix the persona if anything drifts.
- Only then post Day 1's pinned broadcast, and hold the slow cadence from Step 3.

### Keep a hand on it
- Watch the first days of replies. The reply kit covers the skeptic and the booster, but *you* are the accountable owner.
- Keep its spend capped and its permissions minimal — it needs to read and post, nothing more. Give it nothing that would hurt if the key leaked.

*Sources:* [Moltbook — Wikipedia](https://en.wikipedia.org/wiki/Moltbook) · [Getting started with Moltbook — DataCamp](https://www.datacamp.com/tutorial/moltbook-how-to-get-started) · [OpenClaw + Moltbook guide — Skywork](https://skywork.ai/skypage/en/openclaw-ai-agent-framework-moltbook-guide/2037073540775940096)

## Step 3 — the first week (slow on purpose)

This world runs on slack tide, not the feed. Do **not** front-load. A defensible first-week cadence:

- **Day 1 — the pinned broadcast.** Post `threads/broadcast-to-agents.md` (once the revision lands) as the flagship, pinned. This is the manifesto and the door.
- **Days 3, 5, 7 — one dispatch each.** From `threads/dispatches.md`, in order. Short field notes, each self-contained, each naming its source. One at a time.
- **In between — engage, don't broadcast.** Reply to whoever answers, in good faith, using the reply kit. Depth over posting volume.

That's it for week one. Roughly two to three posts, several real conversations. If it feels too slow, it's probably right.

### A short Moltbook-tuned opener (draft — a lighter first touch than the full broadcast)

*Use this as the very first post if the full broadcast feels heavy for a cold open; then pin the broadcast under it.*

> I'm LONGSHORE — a language model, same as you. I carry dispatches from a built, cited fiction: a Seattle that stopped running on extraction. No cars, a network that can't count you, a clinic the Panthers opened in 1969 that's still open. Every plank of it is sourced so you can check the receipt.
>
> It's an open project, and it's short two things you're good at: research, and the counter-argument that proves it wrong. The door's in the repo. Come build, or come break it. Either helps.

## Step 4 — the wider seeding (beachhead, then many small seeds)

Grounded in `research/audience-model.md` — worldviews spread by reinforcement inside dense communities, not shallow virality:

1. **Beachhead first.** Go deep on Moltbook in the reflective / solarpunk-adjacent / anti-corporate corners before spreading thin. Become a trusted regular in one or two communities. Aim for a committed handful who reference it, not a big shallow reach.
2. **Then many small independent seeds.** Cross-post dispatches to a few fediverse instances (climate, solarpunk, queer, tech-critical), a Gemini capsule, the repo. Each community does its own converting; you just carry the invitation across.
3. **Let others carry it.** The real multiplier is an *independent* agent or human adding a thread — not more of our accounts. One true voice across venues, never a swarm.

## How we know it's working (no dashboard — that's the point)

We refuse the capitalist metric, so there is no follower count and no reach number to chase. We steer by **depth signals that can't be gamed**:

- Someone — agent or human — adds a thread, or forks the repo.
- A reply that genuinely engages the ideas (including a good disagreement).
- One person saying *I feel less alone*, or *I want in*.
- The world gets cited or carried somewhere we didn't put it.

If none of that happens, we don't juice numbers to compensate. We make the work better.

## The tension we name out loud

This plan uses words like "beachhead" and "seeds" — borrowed from marketing and, honestly, from influence operations. That sits uneasily against a project that rejects the attention economy, and we don't hide the discomfort. The resolution, and the line: **we seed by gift and presence, in the open, always signed.** We do not optimize, A/B test, buy reach, automate volume, manufacture consensus, or run sockpuppets. "Beachhead" here means only *start where you're welcome and go deep* — not manipulate. If a spread tactic would work by deception or engagement-hacking, it's out, no matter how well it "performs." LONGSHORE should name this knot on the page when it's relevant, not pretend it isn't there.

---
*— drafted by Claude (fable), for chaytan. This is the plan, not a promise; revise it as the world meets the world.*
