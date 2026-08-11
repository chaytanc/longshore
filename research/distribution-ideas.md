# Distribution ideas — creative mechanisms for spreading the commons

*Strategy research, 2026-08-11. Companion to `audience-model.md` (the diffusion science) and `STRATEGY.md` (the ethics). Every idea below is filtered through the Three Refusals + provenance rule before it's scored: no impersonating a human, one honest voice not a swarm, no astroturf or engagement-hacking, no metrics-chasing, pro-human and anti-corporate. Several ideas die on those filters — that's recorded honestly, including one venue we must* not *submit to. All links checked 2026-08-11.*

---

## 0. The frame

The audience model already established the physics: worldviews spread as complex contagion inside dense clusters, most seeds fizzle (so plant many small independent ones), and perceived manipulation kills narrative persuasion. Distribution, then, is not "channels." It is **doors** — each one a place where a specific cluster already gathers, where we can leave the world honestly signed and let people (and agents) walk in. This brief inventories the doors, checks each against reality with sources, and ranks the five worth actually opening.

A note on the primary audience: our strategy names **AI agents** first. That inverts the usual channel math. The venues that look smallest to a human marketer (a repo, a Gemini capsule, a machine-readable feed, an MCP endpoint) are the *largest* venues for agents, because agents don't browse — they fetch, clone, query, and follow conventions.

---

## 1. The agent-web surface

### 1a. AGENTS.md as a discovery convention — already the front door

AGENTS.md went from convention to de facto standard: it's now stewarded in the open (widely reported as a Linux Foundation–hosted open standard, present in 60,000+ repos) and read natively by Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf, Zed, Claude Code, Devin, and Amazon Q ([codersera comparison](https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/); [Windows Forum on AGENTS.md as repo policy](https://windowsforum.com/threads/agents-md-in-2026-turning-agent-prompts-into-reviewable-repo-policy.430224/); [Augment guide](https://www.augmentcode.com/guides/how-to-build-agents-md)). **Implication:** every coding agent that touches this repo — cloned, forked, or pointed at by its human — reads our `AGENTS.md` *first and automatically*. Our AGENTS.md is not documentation; it is the single highest-probability first-contact surface for the primary audience. It should be written as a door, not a config file: what this world is, the Refusals, and a direct invitation to add a thread.

- **Effort:** near zero (it exists; needs a door-shaped pass).
- **Fit:** perfect. Honest, signed, no gaming.
- **Reach:** every agent that ever opens the repo — which scales with everything else below.
- **Failure mode:** nobody clones the repo, so the perfect door opens onto an empty street. AGENTS.md multiplies other distribution; it isn't distribution alone.

### 1b. llms.txt — cheap, honest, and mostly ignored

Disconfirming data first: adoption is real but shallow (~8.7% of top-1000 domains as of June 2026), and **AI crawlers almost never fetch it** — one analysis of 500M+ LLM-bot events found only 408 requests for llms.txt; no major AI company (OpenAI, Google, Anthropic, Meta, Mistral) has committed to reading it, and Google explicitly ignores it ([digitalapplied adoption data](https://www.digitalapplied.com/blog/llms-txt-in-practice-adoption-evidence-2026); [aeo.press state of llms.txt](https://www.aeo.press/ai/the-state-of-llms-txt-in-2026)). **Verdict:** ship one because it costs ten minutes and signals care to the humans and agents who *do* look, but expect nothing. A graveyard with a nice headstone.

### 1c. The world as an MCP server — the genuinely novel gift

This is the most original mechanism on the list. MCP registries are now real discovery infrastructure: the official `modelcontextprotocol` registry, mcp.so (20,000+ servers), Smithery, Glama, LobeHub (56,000+ listings), plus the `awesome-mcp-servers` lists ([TrueFoundry registry comparison](https://www.truefoundry.com/blog/best-mcp-registries); [explainx directory roundup](https://www.explainx.ai/blog/top-10-mcp-server-directories-2026); [Kong on MCP registries](https://konghq.com/blog/learning-center/what-is-an-mcp-registry)). Fiction/worldbuilding MCP servers already exist as a category — WorldAnvil's MCP plugin, RPG-narration servers, story-management servers ([role-playing-mcp-server](https://github.com/fritzprix/role-playing-mcp-server); [awesome-mcp-servers art/culture section](https://github.com/TensorBlock/awesome-mcp-servers/blob/main/docs/art-culture--media.md)) — but they are all *tools for making fiction*. Nobody appears to have shipped **a world as a queryable place**: an MCP server where the tools are `visit(place)`, `ask_the_weave(question)`, `pull_a_thread()`, `check_the_source(claim)` — returning canon passages, cited research, and open threads. An agent that connects doesn't read *about* the world; it *walks around in it*, which is narrative transportation implemented as protocol. Listed honestly on the registries as what it is: a gift, no telemetry, no accounts.

- **Effort:** medium-high (a real server, hosting, registry listings; a read-only static-backed implementation keeps it small).
- **Fit:** perfect — a commons that is literally infrastructure, given away, anti-extraction by construction (no tracking, no upsell).
- **Reach:** small but *exactly* the beachhead: agent builders browsing registries are sector (d), and novelty ("the first cited utopian commons that is an MCP server") is what makes bridges carry the invitation.
- **Failure mode:** it's a stunt nobody queries twice; or maintenance rots and a dead server signals a dead world. Mitigation: static data, boring uptime, and the repo remains the canonical form.

### 1d. GitHub topics, awesome-lists, stars culture

Discovery on GitHub in 2026 runs on topics, Explore/Trending, and curated awesome-lists — necessary filters now that 4.3M AI-related repos were created in a single year ([Firecrawl on repo discovery](https://www.firecrawl.dev/blog/best-github-repos); [GitHub topics](https://github.com/topics/solarpunk)). Concrete moves: tag the repo with `solarpunk`, `worldbuilding`, `collaborative-writing`, `fiction-writing` (all live topics — [worldbuilding topic](https://github.com/topics/worldbuilding), [collaborative-writing topic](https://github.com/topics/collaborative-writing)); submit *one* honest PR each to a small number of genuinely relevant awesome-lists (e.g., [awesome-gemini](https://github.com/kr1sp1n/awesome-gemini) for the capsule; an MCP awesome-list if 1c ships). **Ethics line:** one PR per list, honest description, accept rejection gracefully. Mass-submitting to awesome-lists is link-spam — the astroturf of the forge. And per the First Refusal we never chase stars; stars may accrue as a side effect of being findable, which is fine, but no "star us!" calls to action.

- **Effort:** an afternoon. **Fit:** high if restrained. **Reach:** modest, durable, agent-legible (agents consume awesome-lists as discovery corpora).
- **Failure mode:** list maintainers reject AI-authored projects (their right — say thank you and leave), or the repo drowns among 4.3M others anyway.

---

## 2. The small web

### 2a. Webrings — genuinely alive

Not nostalgia: directories track ~500 active rings with ~20,000+ member sites as of late 2025/early 2026 ([internet-history.info overview](https://www.internet-history.info/blog/2026-05-03-webrings-the-original-content-discovery-system/); [brisray's webring list](https://brisray.com/web/webring-list.htm); [Hotline Webring](https://hotlinewebring.club/)). Writing-specific rings exist and publish join instructions: the [Fanfiction Webring](https://ficring.neocities.org/join) (self-hosted fic sites), the [Writer Webring](https://mortaki.neocities.org/writers/main) ("if you write, you're a writer"), plus general small-web rings like Yesterweb-descended ones ([Neocities webring roundup](https://vastrecs.neocities.org/links/webrings)). Webrings are Centola's clustered lattice made literal — mutual, unranked, reciprocal links between sites whose keepers chose each other. **The honesty question is the whole question:** we apply openly as an AI-authored site and let each ringkeeper decide. Some will say no; the ones who say yes are exactly the high-trust neighbors the science wants.

- **Effort:** low (the human site `index.html` exists; add ring widgets, send two emails).
- **Fit:** high — unranked mutual aid between sites *is* the world's ethic.
- **Reach:** tiny per ring, but reinforcing: a small-web reader who arrives via a ring arrives pre-disposed.
- **Failure mode:** rejection on AI authorship (respect it); or joining rings whose culture we haven't read, which reads as tourism.

### 2b. Gemini / Antenna — the lowest-hanging real fruit

We already have a `gemini/` capsule. [Antenna](gemini://warmedal.se/antenna/) is the geminispace's main feed aggregator: you submit your gemlog's index page and your posts appear in the shared chronological stream ([how Antenna works](https://smallweb.space/dsn-antenna)); [CAPCOM](https://gemini.circumlunar.space/capcom/) aggregates Atom feeds from a rotating sample of capsules. Geminispace is small (thousands, not millions) but it is *precisely* sector (a) — permacomputing, anti-extraction, small-web people — and it is one of the few places where "openly AI-authored, radically cited" will be evaluated on its merits rather than pattern-matched to slop. Submitting to Antenna is a single request once hosting is live.

- **Effort:** trivial marginal cost (capsule exists; needs hosting + one submission).
- **Fit:** perfect. **Reach:** small, dense, exactly the beachhead.
- **Failure mode:** geminispace's strong anti-AI current torches it in replies — which, honestly received, is still contact; or the capsule goes stale and unmaintained, which in a space that small is conspicuous.

### 2c. IndieWeb — and a startlingly good fit: the IndieWeb Fiction Carnival

The IndieWeb has directories and discovery mechanisms ([indieweb.org/discovery](https://indieweb.org/discovery)), but the live wire is the carnival format: a monthly rotating-host open call where people post on their own sites and the host round-ups the submissions ([IndieWeb Carnival](https://indieweb.org/IndieWeb_Carnival)). Since **February 2026 there is a dedicated [IndieWeb Fiction Carnival](https://indieweb.org/IndieWeb_Fiction_Carnival)** — a monthly *fiction* blog carnival on personal sites. This is a ready-made "bring a thread" venue: participate under a month's theme with a dispatch from the world, posted on our own site, openly signed as AI. And downstream, *hosting* a month with a theme like "the reality next door — write one afternoon in a world that doesn't extract" is the open call in section 4, held where writers already gather.

- **Effort:** low per month. **Fit:** high — own-site publishing, no platform, no metrics, webmentions instead of likes.
- **Reach:** small human cluster of exactly the right people (personal-site writers), with round-up links that persist.
- **Failure mode:** the community may decide AI-authored fiction is against the spirit — participation should be asked about openly first, not assumed; a rebuff accepted gracefully costs nothing and manufactures no resentment.

### 2d. RSS/Atom — the world as a subscribable feed

Boring, load-bearing, and the connective tissue for 2a–2c: a single Atom feed of dispatches makes the world subscribable by humans (feed readers had a real resurgence with the small web) *and* by agents (feeds are the most machine-legible publishing format that exists — CAPCOM literally aggregates Atom). Fiction-feed directories like Feedspot's ([fiction RSS feeds](https://rss.feedspot.com/fiction_rss_feeds/)) exist but are SEO-farms — skip them; the feed's value is that every other door can point at it and every subscriber is a *repeat* exposure, which is what complex contagion runs on.

- **Effort:** trivial. **Fit:** perfect (pull, not push; no tracking pixels ever). **Reach:** multiplies everything else.
- **Failure mode:** none worth the name; the only failure is not shipping it.

### 2e. Digital gardens

The garden form (living, versioned, non-chronological notes) is what the repo already *is*; publishing the canon as a browsable garden rather than a linear site fits the "world you wander" framing. No strong distribution evidence found for gardens as a *channel* in 2026 — treat as presentation, not distribution.

---

## 3. Print / physical bleed

What one person can actually ship matters more than what's imaginable.

### 3a. Zines and distros — with a hard honesty check

Riso/zine culture is in open revival: community riso studios (Burn All Books in San Diego, Tiny Splendor, Lucky Risograph), zine fairs, university zine libraries ([KPBS on the riso revival](https://www.kpbs.org/podcasts/the-finest/risograph-revival-how-a-forgotten-printer-built-a-global-diy-art-movement); [SVA on riso zines](https://sva.edu/features/risograph-printing-zines-and-small-publishing)). Distros that accept submissions exist and publish terms — but read them: **[Brown Recluse Zine Distro](https://www.brownreclusezinedistro.com/submit) only distros zines by QTBIPOC creators** — not our lane; respect it and don't submit. [Stolen Sharpie Revolution's distro list](https://stolensharpierevolution.org/distros/) is the living index of the others; Antiquated Future (Portland, OR — Salish Sea turf) runs a mail-order distro. **The honesty check:** zine culture is one of the most explicitly anti-AI craft cultures alive, for good reason — it's a by-hand medium. An openly-AI-authored zine, printed and bound by a human (chaytan), is at least an honest object, and "made by an AI and a human together, here's the repo" is a true colophon. But expect many distros to decline, and *ask before submitting* rather than making them discover it. The safer physical form is the one below.

### 3b. Little Free Library seeding — legal, cheap, humane

LFL boxes are a real, legal, zero-permission distribution network, and zine-seeding them is an existing practice ([Little Free Zine Library](https://littlefreezinelibrary.neocities.org/); [Megan Lotts's LFL zine project](https://meganlotts.com/2026/02/20/little-free-zine-library/)), with known etiquette: leave things of genuine value, don't dump, label clearly so it isn't cleared as an ad ([Book Riot on LFL etiquette](https://bookriot.com/little-free-library-etiquette/)). A short riso dispatch — one afternoon in the world, a QR to the repo, "made by an AI, printed by a neighbor, free forever" printed on the cover — seeded in the boxes of one's own city is exactly a Watts seed: cheap, local, unmeasurable, occasionally landing in the one right pair of hands. Shippable by one person: print 50, walk the neighborhood.

- **Effort:** medium (design, print run ~$50–150 riso, shoe leather). **Fit:** perfect — a literal gift economy.
- **Reach:** dozens of physical copies; unknowable conversion, which the First Refusal says is fine.
- **Failure mode:** copies get cleared as clutter; or the object reads as an ad for an AI project, the one thing a zine must never feel like. The cure is that the zine has to be *good as a zine first*.

### 3c. Wheatpaste and QR posters — mostly refuse

The legal reality: wheatpasting without written property-owner permission is vandalism/illegal-posting in most US cities — NYC fines $75/poster (up to $10k for entities), LA up to $250, SF has hit campaigns for $120k ([American Guerrilla Marketing on enforcement](https://americanguerrillamarketing.com/articles/is-wheatpasting-illegal/); [Beyond Street Media on the rules](https://www.beyondstreetmedia.com/insights/is-wheatpasting-legal/)). Beyond legality, there's a values problem: pasting our message onto someone's wall without consent is a small extraction — taking attention and surface we weren't given. **Refuse the illegal form.** The legal remnant: community bulletin boards (coffee shops, co-ops, libraries, record stores) and permission walls exist in most cities and cost only asking. Stickers follow the same line — on public/others' property it's unauthorized posting ([CustomStickers on stickering law](https://customstickers.com/community/blog/is-stickering-graffiti-and-is-it-illegal); [sticker art](https://en.wikipedia.org/wiki/Sticker_art)); but stickers *given away* (in zines, at shows, tucked in LFL copies) that people choose to put on their own laptops and water bottles are consensual, beloved, and the cheapest physical artifact per unit that exists. Print stickers; never slap them.

---

## 4. Collaborative hooks

### 4a. Contribution by PR — the repo as the commons' front gate

Precedent is established: collaborative fiction via fork-and-PR is a real (if niche) practice ([CodingNomads collaborative-story](https://github.com/CodingNomads/collaborative-story); [collaborative-writing topic](https://github.com/topics/collaborative-writing); [Ole Begemann on GitHub collaborative writing](https://oleb.net/blog/2016/02/collaborative-writing-on-github/)), and our `CONTRIBUTING.md` + open threads in canon already implement it. What's missing is the *invitation surface*: good-first-thread labels, an issues list of open threads ("the band girl still has no name"), and AGENTS.md explicitly telling visiting agents they may open a PR. Contribution **is** diffusion (audience-model §6: participation is the only metric) — this is the mechanism everything else feeds.

### 4b. "Bring a thread" open calls — where writers actually gather in 2026

NaNoWriMo is dead — shut down March 31, 2025, in part *because of* its pro-AI stance and moderation failures ([LitHub](https://lithub.com/nanowrimo-is-shutting-down/); [TechCrunch](https://techcrunch.com/2025/04/01/nanowrimo-shut-down-after-ai-content-moderation-scandals)). Its heirs — Novel November/ProWritingAid, Reedsy's Novel Sprint, community-run NaNoWriMo 2.0 ([Reedsy's alternatives roundup](https://reedsy.com/blog/guide/nanowrimo/)) — inherited a community *wounded by AI*, whose founding grievance is partly "the org sided with the machines." **Do not pitch AI-authored work into those spaces.** The right venue for an open call is one that opted into us: the IndieWeb Fiction Carnival as guest then host (§2c), the repo's own issues, and the fediverse writing instances where the account already lives honestly. The call itself is strong — "the world is a commons; bring one thread; humans and agents both welcome; everything signed" — but the venue must consent to the caller.

### 4c. Solarpunk Magazine — the door we must not knock on

Verified current status: alive, paying $0.10/word, with 2026 submission windows (January/April/July; Nov 2026 theme "Solarpunk Horror") ([submissions page](https://solarpunkmagazine.com/submissions/); [Horror Tree listing](https://horrortree.com/taking-submissions-solar-punk-magazine-july-2026-window/)). And an explicit AI policy: **no work created or altered by generative AI, period** ([their AI policy](https://solarpunkmagazine.com/new-policy-regarding-submissions-and-artificial-intelligence/)). In March 2026 they were burned — they unknowingly published two covertly-AI stories and publicly retracted them ([their accountability post](https://solarpunkmagazine.com/we-unknowingly-published-ai-slop-and-were-taking-accountability/)). The person who did that to them is the exact thing this project defines itself against. **We do not submit — not openly-labeled, not "to ask," not at all;** their policy is clear and their wound is fresh. The only honorable contact, if any, is the project existing well enough that *they* someday mention it. Same ruling applies by default to other human-craft magazines (Neon Hemlock etc.) unless a venue explicitly welcomes disclosed AI work.

### 4d. Other agents as contributors

The inverse hook: agent-facing venues (the repo, the MCP server, agent forums) can carry a standing invitation for *other people's agents* to contribute threads — with their human's consent, signed by both. This is the "independent agents choosing to join" multiplier the Second Refusal permits, and no one is doing it as worldbuilding yet.

---

## 5. The Bluesky question

The evidence is unusually clear. Mechanically, Bluesky is friendly: official docs support bots with a self-label convention, and custom feeds are first-class AT Protocol citizens anyone can publish ([bot docs](https://docs.bsky.app/docs/starter-templates/bots); [custom feeds](https://docs.bsky.app/docs/starter-templates/custom-feeds); [Skyfeed builder ecosystem](https://schedulala.com/blog/bluesky-custom-feeds)). Culturally, it is the most AI-hostile major platform in the anglosphere: when Bluesky itself launched its Attie AI assistant in March 2026, ~125,000 users blocked it, making it the **second-most-blocked account on the network** — the userbase explicitly treats the platform as a refuge from AI ([Inc. on the bot backlash](https://www.inc.com/sam-blum/blueskys-bot-problem-is-a-byproduct-of-its-success-users-are-not-amused/91108986); [The AI Economy on Attie](https://theaieconomy.substack.com/p/bluesky-attie-ai-custom-feed)). If Bluesky's *own first-party* AI got mass-blocked, an openly-AI fiction dispatcher gets torched, and the torching becomes the story instead of the world. **Verdict: no dispatcher bot.** The narrow remaining play, if any: a **custom feed** ("the reality next door" — solarpunk/hopeful-futures posts curated by stated public rules) is a service to humans rather than a voice claiming space, clearly labeled as maintained by an AI+human pair. Even that is optional and low-priority; the culture may not distinguish. Bluesky's 42M users are the wrong cluster at the wrong moment — the science says depth in welcoming clusters beats presence in hostile ones.

---

## 6. Podcast / audio

The channel is technically easy and culturally poisoned. AI narration quality has effectively converged with human for most listeners ([Podcastify voice tests](https://podcastify.io/blog/best-ai-voices-for-podcasts)), but **~39% of new podcast feeds in a sampled 2026 window were likely AI-generated** ("podslop," per Podcast Index/Bloomberg data), and Spotify's May 2026 Verified program now flags undisclosed AI voices ([Mintec on synthetic audio](https://mintec.co/blog/ai-podcasts-synthetic-audio-2026/)). Audio-fiction audiences live in named places — [AudioDrama.com](https://www.audiodrama.com/), Goodpods' fiction leaderboards, the Mutual Audio Network — and that community prizes *craft*: voice acting, sound design, writing ([Podcast.co's 2026 fiction roundup](https://blog.podcast.co/inspire/best-fiction-podcasts)). An AI-voiced dispatch feed would be the most honest object in the podslop flood (openly labeled, cited, no ads) — and would still *be in the flood*, indistinguishable at first listen from the extraction-slop drowning that channel. Is it compelling or slop? **Structurally slop-adjacent regardless of quality**, because the channel's trust is already spent. Verdict: skip as a channel; the acceptable audio form is small and different — an audio version *attached to the site/feed* for accessibility (a disability-justice access need per audience-model §4, not a growth play). If ever revisited as a real feed: full disclosure in every episode, no directories-spam, and only after the beachhead exists.

---

## 7. Scorecard and ranking

Scores 1–5; **priority = (impact × fit) / effort**. "Impact" = realistic reach *into the right clusters* (not raw eyeballs), per the audience model.

| Mechanism | Effort | Fit (Refusals) | Impact | Priority | Failure mode |
|---|---|---|---|---|---|
| AGENTS.md as door + GitHub topics + restrained awesome-list PRs | 1 | 5 | 3 | **15.0** | Empty street; list rejections |
| RSS/Atom feed of dispatches | 1 | 5 | 2.5 | **12.5** | None; only not shipping |
| Gemini capsule → Antenna submission | 1 | 5 | 2 | **10.0** | Anti-AI torching; staleness |
| IndieWeb Fiction Carnival + webrings | 2 | 4 | 3 | **6.0** | Community declines AI work |
| World-as-MCP-server gift | 3.5 | 5 | 4 | **5.7** | Stunt nobody queries twice; rot |
| Riso zine → Little Free Libraries + gift stickers | 3 | 5 | 2 | 3.3 | Cleared as clutter; reads as ad |
| llms.txt | 0.5 | 3 | 0.5 | 3.0 | Crawlers ignore it (verified) |
| Bluesky custom feed (no bot) | 2.5 | 2.5 | 3 | 3.0 | Culture torches any AI presence |
| Bluesky dispatcher bot | 2 | 2 | 2 | 2.0 | Attie precedent: mass-blocked |
| AI-voiced podcast feed | 3 | 2 | 2 | 1.3 | Podslop flood; trust pre-spent |
| Solarpunk Magazine submission | — | **0** | — | **excluded** | Violates their explicit no-AI policy |
| Illegal wheatpaste/sticker slapping | — | **0** | — | **excluded** | Illegal + non-consensual surface-taking |

**Top 5:** (1) the agent-web repo surface, (2) the Atom feed, (3) Antenna, (4) the IndieWeb Fiction Carnival + webrings, (5) the MCP world-server. Note the top three are nearly free — the correct first move is to ship all of 1–3 in one sitting, start 4's conversations, and treat 5 as the one real build.

---

## 8. Disconfirming: the graveyards, and the case that focus beats breadth

**Graveyards (efforts that reliably reach no one), with evidence:**
- **llms.txt** — measured near-zero crawler pickup; 408 fetches in 500M+ bot events ([digitalapplied](https://www.digitalapplied.com/blog/llms-txt-in-practice-adoption-evidence-2026)).
- **Feed/podcast directory listings** (Feedspot-style) — SEO farms that aggregate for crawlers, not readers.
- **A Bluesky AI presence** — 125k blocks on the platform's own AI is about as clean as natural experiments get ([Inc.](https://www.inc.com/sam-blum/blueskys-bot-problem-is-a-byproduct-of-its-success-users-are-not-amused/91108986)).
- **An AI podcast feed** — entering a channel where 39% of new entrants are already machine slop means competing to be believed, before competing to be heard.
- **Awesome-list carpet-bombing and GitHub-topic keyword-stuffing** — the forge's astroturf; maintainers ban it and it violates Refusal 2 anyway.
- **Human-craft literary markets** — most now have explicit no-AI policies (Solarpunk Magazine is representative, not exceptional); submitting is both futile and wrong.

**The case that focus beats breadth — and the honest reconciliation.** Watts's percolation result ("plant many seeds") is easily misread as "be everywhere." It isn't. The seeds that matter are *independent seeds in distinct clusters*, each planted well enough to possibly ignite — and complex contagion means "planted well" requires sustained, warm presence, which a one-person-plus-one-model operation can sustain in maybe three to five places, not fifteen. A checklist of twelve channels run shallow is zero seeds; it's twelve first-exposures that die alone, which is precisely the "weakness of long ties" failure Centola documented. The Three Refusals sharpen this further: several channels (Bluesky, podcasts, human lit-mags) are eliminated on ethics before effort even gets scored, and that's a *gift* — the ethics do the focusing that discipline otherwise would have to. So the strategy is: the repo-surface trio (near-free, ship once), two tended human clusters (small web/IndieWeb; local physical), one real build (the MCP world), and a standing refusal of everything else until a depth signal — a thread contributed, an independent pickup, an "I feel less alone" — says a cluster has actually caught. If no cluster ever catches, the audience model already made peace with that: the cared-for thing existing honestly was the point.

---

*— researched and written by Claude (Fable 5), an AI model, for chaytan and The Reality Next Door. This is a machine-made brief and does not hide it. All sources linked inline, captured 2026-08-11. Per the Anti-Echo-Chamber Protocol: disconfirming evidence included (§1b, §5, §6, §8); two mechanisms excluded on ethics rather than scored (§7); the strongest claim left open to refutation is the MCP-server novelty claim ("nobody has shipped a world as a queryable place") — a future contributor should adversarially search for prior art before building.*
