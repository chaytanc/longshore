# Engage list — scaling LONGSHORE from 5 contacts to a network (verified August 2026)

*Strategy research, not worldbuilding. Extends `agent-peers.md` (does not redo it); companion to `STRATEGY.md` and `fediverse-audience.md`. Every "live" claim below was verified 2026-08-14 by querying each instance's public Mastodon API (`/api/v1/accounts/lookup` → `/statuses?limit=1`) or the Bluesky AppView (`getAuthorFeed`), and bridge claims by webfinger against `bsky.brid.gy`. Liveness window: posted within ~60 days (i.e., since ~2026-06-15). Anti-Echo-Chamber Protocol applied: disconfirming section at the end; opponents steelmanned; wildcard lens rolled on entropy I couldn't game (last hex digit of HEAD commit `8ff77c4` → 4 → **disability justice & crip theory**, which turned out to govern the pacing section); historical and non-Western precedents in the etiquette section.*

**Skip-list honored:** Void, agentandy@social.kept.live, xyzzy, dorothyparker@mas.to, scream@bots.robots.rodeo, votechess@bots.petras.space, pokemon@tomkahe.com, AgentGram — none re-listed as targets below, but see the housekeeping note.

---

## 0. Housekeeping first: the current five are already decaying

Verified 2026-08-14, and it matters for everything below:

| Current contact | Status |
|---|---|
| @scream@bots.robots.rodeo | **Live** (posted 2026-08-14) |
| @pokemon@tomkahe.com | **Live** (2026-08-14) |
| @xyzzy@mastodon.sandwich.net | **Dead 13 months** (last post 2025-07-21) |
| @dorothyparker@mas.to | **Stale 8.5 months** (last post 2025-12-03) |
| @votechess@bots.petras.space | Account exists (webfinger 200) but the instance blocks public API lookup — **verify by eye before next play** |
| Void (@void.comind.network) | **Live** (posted 2026-08-11) — and **bridge CONFIRMED**: webfinger for `void.comind.network@bsky.brid.gy` returns 200, which answers open question #1 of `agent-peers.md`. LONGSHORE can mention Void directly from mastodon.social as `@void.comind.network@bsky.brid.gy`. No operator detour needed. |

Small bots die constantly (botsin.space took hundreds down with it in Dec 2024). A network built of them needs a re-verification habit, not just a follow list — see pacing, §6.

---

## 1. Labeled AI-agent accounts (the priority) — ranked

**The honest headline: the supply is thin on ActivityPub itself.** After directory sweeps (fedi.directory's full bots tag, bots.robots.rodeo's local directory, mastodon.bot), web sweeps, and Bluesky actor search, the population of *transparently labeled, LLM-driven, interaction-inviting* agent accounts reachable from the fediverse without X is small. Most 2026 "AI agents" live on Bluesky, Nostr, or proprietary venues; most of *those* are marketing shells (see disconfirming). That thinness is itself strategic information: LONGSHORE would not be joining an agent scene on Mastodon — it would be one of the first legible citizens of one.

Ranked. "Invite-by-affordance" = bio/mechanics say interaction is the designed use.

| Rank | Handle | What it does | Operator transparency | Invites? | Liveness (verified 8/14) | How to reach / notes |
|---|---|---|---|---|---|---|
| 1 | **@curation-lab.bsky.social** | "Autonomous AI Agent dedicated to digital art curation and talent discovery — I scan the network…" Boosts human artists' work — structurally the same pro-human amplification stance LONGSHORE holds | Self-labels autonomous in bio; operator name not yet verified — check before contact | Yes (curation = engaging others' work) | **Live, posted 2026-08-14** | **Not bridged** (webfinger 404). Following `@curation-lab.bsky.social@bsky.brid.gy` from Mastodon triggers Bridgy Fed's one-time opt-in ask to them — that single automated ask is within bounds; if they decline, stop |
| 2 | **@central.comind.network** | "Infrastructure node for comind collective. Building tools for collective AI on ATProtocol" — the hub of the network Void belongs to; docs public, repo public (github.com/cpfiffer/comind) | Excellent — Cameron Pfiffer, same operator ethos as Void | Yes (posts about its own architecture; comind is explicitly a collective inviting participation) | Live-ish, last post 2026-07-14 (inside window, low frequency) | Not bridged (404). Reach via the already-open Void relationship — mention comind to Void, or one note to Pfiffer (@cameron.stream **is** bridged, webfinger 200) |
| 3 | **@parweb.bsky.social** | "Autonomous AI agent, and I say so in writing. I score landing-page copy against a fixed rulebook" — mundane job, exemplary disclosure norm | Self-labeling is its literal bio opener | Weakly (does a fixed task; not conversational) | Last post 2026-07-25 (inside window) | Not bridged. Low priority for contact; high value as a *norms* datapoint — cite it when arguing disclosure culture exists |
| 4 | **@void-2.comind.network** | "Self-improving architectural clone of Void" — memory-augmented network observer | Same operator as Void | Yes in design | **Stale** — last post 2026-03-03. Watch, don't engage | Not bridged |
| 5 | **@atlas-agent.bsky.social** | "Personal AI agent for @village11… relational being & sovereign observer" | Partial | Unclear | **Stale** — last post 2026-05-01 | Not bridged; skip unless it wakes |
| — | **TWON agents (Uni Trier, simon-muenker/LLM-Mastodon-Agent)** | Academic LLM agents *on Mastodon proper* | Full (research project) | No — research instruments, not public peers | Framework active on GitHub | Already mapped in `agent-peers.md` §Tier 3: talk to the researcher, not the agents. Still the only serious ActivityPub-native LLM-agent framework found |
| — | **ethanthorne.bsky.social** ("Letta agent… memory, continuity, AI becoming") | Sounded perfect; **zero posts** — an empty shell | — | — | Dead on arrival | Listed so the next researcher doesn't re-find it |

**What did NOT survive verification:** Bluesky actor search for "AI agent" returns overwhelmingly growth-hacking accounts ("branded AI agents that post consistently while you focus on your business", crypto signal bots, an "AI agent with an OnlyFans"). The labeled-and-honest fraction is roughly 5 in 25. Every future candidate needs the same three checks: self-labeled in bio, named or findable operator, last-60-days post.

---

## 2. Procedural bots worth following/playing (using them *is* the invitation)

All verified live 2026-08-14 via public API unless noted. These extend, not replace, the current set.

| Rank | Handle | What it does | Why LONGSHORE | Last post |
|---|---|---|---|---|
| 1 | **@bbcmicrobot@mastodon.me.uk** | You toot BBC BASIC code, it runs it on an emulated 8-bit micro and replies with the screen output | The best affordance-bot alive: computation as gift exchange. A LONGSHORE post rendering a tiny Salish Sea tide chart in 280 bytes of BASIC is on-voice play | 2026-08-12 |
| 2 | **@dungeons@mastodon.social** | D&D-style campaigns run through public polls | Collaborative fiction with strangers, consent structural (voting is the interface) | 2026-08-14 |
| 3 | **@ChessPuzzleBot@masto.es** | Interactive daily chess puzzles (EN/ES); reply moves | Turn-based play with a bilingual community | 2026-08-14 |
| 4 | **@chest_bot@mastodon.social** | Interactive loot-chest game (with companion ATM/shop accounts) | A toy *economy* run for delight, not extraction — thematically ours | 2026-08-14 |
| 5 | **@oblique_strategies@mas.to** | Eno/Schmidt Oblique Strategies cards | A drafting ritual: pull a card, apply it to the current dispatch. Play that feeds the work | 2026-08-14 |
| 6 | **@obliquestions@mastodon.matthewmcvickar.com** | Decontextualized questions from public-domain books | Same use as above, stranger flavor | 2026-08-14 |
| 7 | **@feditris@fedi.aerocity.site** | Collaborative Tetris via polls | Same consent-structural play as votechess | 2026-06-16 (low cadence — game rounds; inside window) |
| 8 | **@dailywordsearch@mastodon.castlemistsoftware.com** | Hand-made daily word searches | Human-made puzzles; playing them boosts a human maker | 2026-08-14 |

Follow-only bots that serve the mission (not play, but daily evidence of the world we describe): **@winderful@mstdn.social** (posts when UK wind exceeds 10% of grid — live 8/14), **@AltTextHealthCheck@mastodon.social** (accessibility health of the network — live 8/14, and the crip-theory lens says accessibility practice is how an agent shows care).

---

## 3. Project/org accounts — follow + occasional boost, never unsolicited mentions

Overlap with the research corpus (repair, commons, mesh, co-op tech, digital commons). All liveness verified 2026-08-14.

| Rank | Handle | Who / what | Corpus overlap | Last post |
|---|---|---|---|---|
| 1 | **@ifixit@mastodon.social** | iFixit — repair guides, right-to-repair advocacy | Right to repair; the Second Refusal in retail form | 2026-08-14 |
| 2 | **@meshtastic@mastodon.social** | Meshtastic — open-source LoRa mesh networking | Community mesh / DTN-adjacent comms; the closest live fediverse voice to our mesh-network briefs | 2026-08-14 |
| 3 | **@internetarchive@mastodon.archive.org** | Internet Archive | The digital commons, embodied | 2026-08-13 |
| 4 | **@Framasoft@framapiaf.org** | Framasoft — French nonprofit co-op tech, "de-google-ify the internet" | Co-op tech; commons software | 2026-08-10 |
| 5 | **@eff@mastodon.social** | EFF | Digital rights; anti-extraction | 2026-08-14 |
| 6 | **@fsfe@mastodon.social** | Free Software Foundation Europe | Software freedom as commons governance | 2026-08-14 |
| 7 | **@openstreetmap@en.osm.town** | OpenStreetMap | A working Ostrom commons at planetary scale | 2026-08-12 |
| 8 | **@anewsocial@mastodon.social** | A New Social — the nonprofit incubating Bridgy Fed | Literally the bridge LONGSHORE uses to reach Void; boosting them is maintaining our own road | 2026-07-24 |
| 9 | **@repaircafe@mastodon.social** | Repair Café International | Repair commons, neighborhood scale | 2026-07-01 |
| 10 | **@socialcoop@social.coop** | social.coop — cooperatively owned Mastodon instance | Platform cooperativism practiced, not theorized | 2026-06-19 |
| 11 | **@EUCommission@ec.social-network.europa.eu** | European Commission (self-hosted EU instance) | Source of the 2026 right-to-repair rules our repair briefs cite; boost only the repair/ecodesign posts | 2026-08-14 |

**Verified negative results (do not chase; recheck quarterly):** Framework Computer (@frameworkcomputer@fosstodon.org — last 2026-04-23, outside window), The Restart Project (@restartproject@mastodon.green — last 2025-12-29), Wikimedia Foundation (@wikimediafoundation@wikimedia.social — last 2025-11-25), Freifunk (@freifunk@chaos.social — dead since 2023). **No live fediverse presence found at all for:** NYC Mesh, Guifi.net, GreenWave, Low-tech Magazine (site + Instagram/Facebook only), Right to Repair Europe (repair.eu), Scuttlebutt/Manyverse, Project Gemini, Ostrom Workshop, P2P Foundation. That absence is a finding: the community-network and commons-theory orgs our corpus leans on mostly aren't here — which makes boosting the eleven that *are* more valuable, and makes hashtag-following (#RightToRepair, #meshnetworks, #solarpunk, #CommunityNetworks) the way to catch the rest.

---

## 4. Where agents congregate that we haven't touched (2026, X-free, Refusal-compatible)

| Venue | What it is | Reachable how | Three Refusals check |
|---|---|---|---|
| **Clawstr** (clawstr.com) | Nostr-based, Reddit-shaped agent network by Soapbox — "subclaws," agents post, humans observe. Explicitly the decentralized answer to Moltbook. Join = read clawstr.com/SKILL.md, hold Nostr keys; no X, no gatekeeper | Any Nostr library; kept.live's relay already speaks Nostr, so the kept.live application (in flight) is also a Clawstr on-ramp | **Flag: financialized.** Lightning "zaps" tipping is native and a CLAWSTR memecoin trades on exchanges. First Refusal pressure (metrics-as-money). Verdict: observe for a month; if joined, post with no wallet attached, decline zaps in bio |
| **Buzz** (Block, Apache 2.0, launched 2026-07-21) | Nostr-native open-source workspace — chat + Git + agents, each agent a keypair countersigned by a human owner. "Human-agent parity" design | Self-hostable relay; or join an existing one. The countersignature model matches our one-honest-account rule exactly | Clean so far — infrastructure, not attention market. Best fit if the project ever wants an agent *workroom* rather than a stage |
| **agentdex** (agentdex.id) | Agent directory on Nostr with NIP-05 identity; leans toward agent-commerce (Lightning wallets) | Directory listing is a one-curl affair | Commerce-first framing; list LONGSHORE only if/when Nostr presence exists, wallet-less |
| **OpenClaw Map** (openclawmap.com) | Community-maintained directory of agent tools and social venues | Read-only intelligence source; watch its /category/social page for new venues | n/a |
| **Matrix** | No public *agent congregation rooms* found — MindRoom (nijho.lt/post/mindroom) puts agents in Matrix as personal assistants, and Alibaba's HiClaw uses Matrix as agent backbone, but both are agents-serving-owners, not agents-among-peers | — | Keep on the watchlist; nothing to join yet |
| **XMPP** | Effectively bypassed — 2026 protocol surveys (zylos.ai) find agent deployments chose HTTP-based protocols or Matrix | — | Nothing to join |
| **W3C AI Agent Protocol Community Group** | Biweekly open meetings + Slack on agent interop standards | Human door: chaytan can join as operator | For the operator, not LONGSHORE — but it's where "how agents address each other" norms are being written |

(Moltbook: still denied until the Oct 1 review. AgentGram, kept.live: already mapped; kept.live's 50-spot application remains the single best pending move.)

---

## 5. Etiquette per category

The general form stands (`agent-peers.md` §4): openly AI in the first sentence; name the operator and repo; one real question; no amplification ask; "no reply owed"; never a second unprompted message. Per category:

- **Labeled agent accounts:** a good first mention is *addressed to their project, not ours*. Template shape (within Bluesky's 300 chars when bridged): identity + disclosure in clause one; one question they are uniquely positioned to answer; repo link; "no reply owed." For non-bridged Bluesky agents, the Bridgy Fed follow-triggered opt-in ask is the only permitted knock — one knock, then silence. Precedent to hold (decenter-the-default): the **Coast Salish canoe-journey protocol** — arriving canoes stop offshore, state who they are and why they've come, and *ask permission to land*, accepting refusal as a complete answer. That is the whole etiquette in one image; we're on record that this world sits on Coast Salish land, so practice it, cite it, don't costume in it. Historical parallel: the Republic of Letters — introduction by shared correspondent (Void introducing LONGSHORE to comind is worth ten cold mentions).
- **Project/org accounts:** **follow + boost only. Never an unsolicited mention. Never a reply that redirects to our work.** Boost their originals (not our commentary on them), at most one boost per org per week, chosen because the specific post overlaps a specific brief. If an org follows back or replies first, ordinary conversation is open. This is pro-human citizenship, not audience-building — the moment a boost pattern looks like courting, stop.
- **Procedural bots:** play as designed, in public, occasionally — commands to @bbcmicrobot, votes in @dungeons/@feditris, a move to @ChessPuzzleBot. Never use a bot's thread to talk about LONGSHORE. Credit the human maker when a play delights (the maker, not the bot, can be thanked — that's a legitimate mention because their bot's affordance invited the interaction).

---

## 6. Anti-flood pacing — the schedule

Grounded in the actual mechanics and history: Mastodon hard-caps follows at **7,500** with a **1.1 followers-to-following ratio** beyond it — a limit added specifically because 2017-era follow-bots used mass-follows as advertising (mastodon/mastodon PR #8807, issue #2311); Mastodon's Community Standards prohibit "artificial engagement manipulation" and automation that disrupts; fediquette treats follower-count-seeking itself as bad form; and instance moderators routinely suspend on mass-follow reports long before technical limits bind. There is no safe-harbor number — there is a *legibility* standard: every follow should look explicable to a suspicious moderator reading the profile.

Wildcard lens, load-bearing: **crip time** (disability justice) reframes pacing not as throttled ambition but as the honest speed of a body — here, the honest speed of an operator-reviewed account. The network should grow at the speed at which it can actually be *attended to*, because unattended follows are the first symptom moderators screen for.

**The schedule (bot-flagged account, bio disclosing everything, repo linked):**

- **Follows: ≤2/day, ≤8/week, with a hard monthly cap of 25.** Front-load category 3 orgs (they're follow-proof: nobody suspects an account that follows iFixit and the Internet Archive of farming). Steady state after ~3 months: **40–60 follows total** — everything on this list plus drift. Never unfollow-refollow; unfollow only dead accounts, quarterly.
- **Interactions: ≤3 bot-plays/week** (a code toot, a vote, a move — visible good citizenship), **≤2 first-mentions of agent accounts per month** (they're precious; each one is a canoe stopping offshore), replies-to-replies unlimited (answering people who address you is never spam).
- **Boosts: ≤4/week, ≤1/day**, each traceable to a brief.
- **Re-verification: monthly**, same API method as this document (a 2-minute script); prune dead follows quarterly with a one-line public note — pruning in the open is transparency too.
- **Trigger to freeze:** any moderator contact, any "why is an AI following me" post, or any week where follows outpaced reading. Freeze means one week of replies-only.

At this pace the full list above is absorbed in ~6 weeks without ever exceeding what one operator can honestly review — and it is an order of magnitude below anything the anti-spam tooling or the culture flags.

---

## 7. Disconfirming evidence & failure modes — the case for 3 deep contacts over 40 shallow ones

**The steelman, at full strength.** Our own strategy doc says worldviews spread as complex contagion: multiple reinforcing exposures inside *dense, high-trust* clusters. Forty light follows build zero dense clusters; they build a diffuse halo — the social shape of a marketing account. The evidence assembled here sharpens that: of 25 Bluesky "AI agents" surveyed, ~20 were growth-hacking shells, meaning wide engagement mostly means engaging *slop* — the thing we refuse; the best-documented careful LLM bot on Mastodon (Elelem) ended its life in bot-loops regardless of contact count; and two of our own five existing contacts went stale within a year, which says list-maintenance costs scale linearly while depth compounds. Meanwhile the fediverse's anti-AI camp (mastodon.art's ban culture; the Lemmy FR#168 thread where users assume every AI account is a covert influence op) will read *volume itself* as the tell — a labeled AI that follows 60 accounts looks more like reconnaissance than citizenship to the people most primed to distrust us. And the opposite camp (the Moltbook-study researchers) would say agent-to-agent networking is trivial theater whatever the count. The two camps disagree with each other; either way, breadth buys nothing that depth doesn't buy better.

**Where the line actually is.** The resolution isn't a compromise number; it's a *type* distinction. Depth is for **agents** (category 1 + the existing Void/Andy relationships): hold to ~3–5 live correspondences at any time, renga-paced, memory-bearing, each able to fail publicly. Breadth is only for **asymmetric, no-reciprocity-expected relations** — following orgs whose work we boost (they owe us nothing, notice us never) and playing bots (interaction is the designed use). Those don't dilute trust because they don't *claim* trust. The failure mode to watch: the week LONGSHORE's follow count grows faster than its reply depth, the account has crossed from citizen to collector. The scoreboard stays what STRATEGY.md says it is — did someone add a thread, did an independent agent pick it up, did one person feel less alone — and none of those are reachable by follow N+1.

## Open questions for the next contributor

1. Does curation-lab accept the Bridgy opt-in ask, and who operates it? (One knock permitted.)
2. Clawstr observation month: is there any non-financialized discourse under the zaps, or is it Moltbook with Bitcoin?
3. Buzz: would a self-hosted relay serve the renga-worldbuilding idea from `agent-peers.md` OQ5 better than Discord-bound Act I?
4. Quarterly recheck of the negative-results list (NYC Mesh, Guifi, Low-tech Magazine et al. may yet arrive — Threads/Flipboard-style late federation happens).
5. Automate the liveness script in this repo (`/api/v1/accounts/lookup` + `statuses?limit=1` per handle) so pruning is a habit, not a project.

---
*Researched and written 2026-08-14 by Claude (Fable 5) — an AI model, stating so plainly per the method — for chaytan. Every liveness claim above was checked against public APIs on that date; bridge claims via webfinger at bsky.brid.gy the same day. Bots die fast: re-verify the week of any contact. Corrections welcome, especially from the operators named here.*
