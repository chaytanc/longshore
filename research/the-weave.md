# Research brief: The Weave — non-extractive communication networks

*A grounding document for the Weave (CANON.md §"The Weave"). Everything below is real: real protocols, real projects, real researchers, real numbers where they exist. The point is to make the fiction load-bearing — the Weave should feel like something a Salish-Sea engineer could actually stand up, because most of its parts already exist.*

---

## 0. The thesis in one breath

The internet we have is not the only internet that was ever technically possible. The Weave is what you get if you keep four things we already know how to build — **store-and-forward delivery**, **community-owned physical infrastructure**, **federated open protocols**, and **commons governance** — and deliberately *subtract* the three things the attention economy added on top: **the algorithmic feed, the reach metric, and the surveillance business model.** Nothing below requires inventing new physics. It requires refusing to build the parts that count you.

---

## 1. The problem the Weave is a refusal of

The Weave only makes sense against what it rejects. The critique is well-documented and worth citing precisely, because it tells us exactly which affordances must be *engineered out*.

- **Shoshana Zuboff, *The Age of Surveillance Capitalism* (2019).** Coins "surveillance capitalism": "the unilateral claiming of private human experience as free raw material for translation into behavioral data." Her key concept is **behavioral surplus** — data exhaust beyond what's needed to provide the service, captured and sold as "prediction products." The load-bearing insight for us: the harm is not screens or connection; it is the *business model* that turns human experience into raw material. Remove the extraction incentive and most of the pathology has nothing to feed on. (Harvard Business School; *Age of Surveillance Capitalism*.)
- **Zeynep Tufekci** — attention as the scarce resource platforms compete to capture; algorithmic amplification systematically favors outrage, novelty, and extremity because those maximize engagement, not because anyone chose them. Engagement-optimization is an *emergent* value system nobody voted for.
- **Tristan Harris / "Time Well Spent"** lineage — the specific UI mechanics of capture: infinite scroll, pull-to-refresh (a literal slot-machine variable-reward schedule), red notification badges, "someone is typing," visible like/follower counts as social-proof dopamine loops.

**Design consequence (this maps directly onto CANON's Three Refusals):** the Weave forbids, at the protocol level, the three things that make capture possible:
1. **No reach metric.** You cannot learn how many saw your thread. (Kills the "creator" incentive gradient and the comparison that drives compulsive posting.)
2. **No ranking authority.** No node has the right to decide the order in which anyone sees anything. Order is a property the *reader* sets, not the network.
3. **No behavioral surplus.** Relays are forbidden from logging who-read-what beyond what's needed to route and de-duplicate, and that log is ephemeral. There is no observer with a god's-eye view of the graph, so there is nothing to sell and nothing to optimize against.

---

## 2. Store-and-forward: the Weave is "very slow, very warm mail," and that's a real architecture

CANON says the Weave travels "by hop, human and machine relays," with answers coming back "over days or weeks, heavier for the wait." This is **Delay/Disruption-Tolerant Networking (DTN)** — a mature, standardized field.

- **RFC 4838 (2007), *Delay-Tolerant Networking Architecture*** and **RFC 9171 (2022), *Bundle Protocol Version 7*** (superseding RFC 5050) define the standard. DTN was built for exactly the conditions the Weave embraces: links that are intermittent, high-latency, and never guaranteed end-to-end. NASA uses it for deep-space and Mars comms (there is no continuous link to Mars; you *store and forward*).
- **The core primitive is the "bundle."** Instead of assuming a stable path from sender to receiver, each node uses **store, carry, and forward**: it accepts a bundle, holds it (possibly for a long time), and hands it onward when a next hop becomes available. A node "promises to keep the data until the next node acknowledges receipt." No continuous route ever has to exist. This is *precisely* CANON's "travels by hop... answers come back over days or weeks."
- **Open implementations exist**: **DTN7** (open-source Bundle Protocol 7), and **The ONE** simulator for evaluating DTN routing.
- **Sneakernet / data mules are first-class, not a fallback.** In DTN, "intermediate nodes act as data mules, physically carrying data around until it reaches its destination." Research has proposed using the **Swiss rail network as a data-mule backbone**. In a world where a tram or a sailing packet crosses the Sound every afternoon, *the vehicle is the network.* A USB-scale relay riding the 4pm foil-ferry is a legitimate Weave hop.

**Routing without a central map** is also solved, in multiple flavors — and critically, none of them require a global index of who's out there:
- **Epidemic routing** — flood copies to every node you meet; maximizes delivery probability at the cost of bandwidth. Good for the "is anyone out there" broadcast.
- **Spray-and-Wait** — release only *L* copies, then let those carriers deliver directly. Bounded, polite flooding.
- **PRoPHET** — routes by *delivery predictability* estimated from the history of past encounters. Nodes you meet often, and nodes *they* meet often, are better bets. This is a mathematical formalization of "ask around; someone always knows someone."
- **Social/opportunistic routing** — later work (e.g., "Beyond Traditional DTN Routing: Social Networks for Opportunistic Communication") routes along *human* social ties. This is the honest engine under CANON's "difference is a resource the world routes toward": the network literally hill-climbs toward the person most likely to know a person like you.

---

## 3. The physical layer already has community-owned precedent

The Weave needs wires and radios owned by nobody-for-profit. This exists, at scale, today.

**Community mesh networks (the Weave's local nervous system):**
- **Guifi.net** (Catalonia) — the world's largest community network, tens of thousands of km of links, fiber + wireless in P2P, P2MP and mesh modes. Crucially it is **not owned by a company or a government; it is a commons** governed by a **community license (the "Compact for a Free, Open and Neutral Network," XOLN)**: whatever you attach to the network stays part of the commons. Local installers earn a living doing maintenance and pay a percentage back to the Guifi Foundation — *money is thin, local, and boring; the infrastructure is the thick layer.* (This is CANON's Third Refusal, already implemented.)
- **NYC Mesh** — volunteer-run; a hybrid of point-to-point, sector antennas, ethernet, fiber, and mesh, with "supernodes" on tall buildings. Anyone can request an install and join; it is deliberately non-commercial.
- **Freifunk** (Germany) — hundreds of local free-radio communities running open firmware; a culture of *sharing* bandwidth as a civic act.

**The radio primitive for the un-wired stretches:**
- **Meshtastic** over **LoRa** — cheap (~$30) solar-capable radios that form a self-healing text mesh. Long range (2–5 km typical, 15+ km line-of-sight, 100+ km via multi-hop), *very* low power, fully off-grid, open source and 100% community-driven. Each node rebroadcasts for its neighbors. This is a literal, buildable "human and machine relays" fabric that survives when everything centralized is down. Perfect for island-to-island and boat-to-shore hops on the Salish Sea.

**The backhaul, where you still need one:**
- **Municipal & cooperative ISPs.** Chattanooga's **EPB** built the largest municipally-owned fiber-to-the-home network in the US (10 Gbps), funded by municipal bonds + a 2009 federal grant, and now *partners with* smaller towns and co-ops. **Rural electric cooperatives** (a 1930s New Deal institution) are re-running the same play with fiber. Precedent: essential infrastructure can be owned by the people it serves and run at cost, not for extraction.

---

## 4. Federation and the "small web": proof that un-ranked, un-metered social space works

The Weave's *content* layer — threads, replies, works — has direct living ancestors.

- **ActivityPub (W3C standard, 2018)** and the **Fediverse** (Mastodon et al.). The decisive fact for us: **the timeline is chronological and consent-based — there is no algorithm.** You see posts from accounts you followed, newest first, full stop. Mastodon's own framing: "no dopamine-driven algorithms." **Federation** means no single server owns the graph; instances interoperate over an open protocol and can defederate abusers. This is the Weave's governance shape in miniature: many small, human-scale, independently-run nodes speaking a common tongue.
- **IndieWeb** — "own your content"; your identity is your own domain, not a platform account. Principles: *own your data, publish on your own site, syndicate elsewhere (POSSE).*
- **The Gemini protocol** and the **"small web."** Gemini is a deliberately *minimal* alternative to HTTP: **no cookies, no tracking pixels, no third-party resources, no behavioral analytics** — tracking is not restricted, it is *impossible by construction.* "Geminispace fosters a culture focused on sharing knowledge and creativity rather than monetization and growth metrics." This is the purest existing proof that a network can be technically incapable of surveilling you. The Weave's document format should inherit this: **capability-minimalism as a safety property.**
- **Secure Scuttlebutt (SSB)** — the closest existing thing to the Weave's actual mechanics. An **offline-first, hostless, gossip protocol**: every person has a signed **append-only log**; devices find each other over the LAN and **sync when they meet**; "Pub" nodes help bridge across the internet but are not authorities. You carry your whole social world on your device and it reconciles opportunistically with whomever you encounter. SSB is store-and-forward social networking that *already* has no central server, no global feed, and no reach count. It is the Weave's grandparent.

---

## 5. Governance: Ostrom, because a commons that isn't governed gets enclosed

A network owned by everyone is owned by no one unless it is *governed* — otherwise it's captured or it collapses (the free-rider problem: "resources are offered for free, nobody is incentivized to contribute back"). **Elinor Ostrom** won the 2009 Nobel in Economics for showing that communities *do* sustainably govern common-pool resources, and for extracting the **eight design principles** they share. They map astonishingly cleanly onto a network commons (Guifi.net is literally studied as a CPR):

1. **Clearly defined boundaries** — who is in the commons and what the resource is. *(Weave: you opt in; membership is a real, human act.)*
2. **Rules fitted to local conditions** — no one global rulebook. *(Each locale's Weave sets its own norms.)*
3. **Collective-choice arrangements** — those affected by rules help make them.
4. **Monitoring** — by the community, of the community.
5. **Graduated sanctions** — first offense is a word, not a ban; escalation is proportionate.
6. **Cheap, fast conflict resolution.**
7. **Minimal recognition of the right to self-organize** by outside authority.
8. **Nested enterprises** — small units federated into larger ones (block → neighborhood → bioregion → world). *This is exactly the federation topology, and exactly CANON's "Never centralize."*

Ostrom is the antidote to the one thing that would break the Weave: the temptation to build a single index "just to make it usable," which is how every commons gets enclosed. **The Weave stays decentralized not by luck but by governance design.** Contemporary work applies these principles to data commons (Mozilla Foundation), open-source projects (Nathan Schneider / "governable stacks"), and open-data ecosystems.

**Right to repair** is the physical-layer expression of the same ethic (CANON's Second Refusal, "no erasure to enable replacement"). By 2025, right-to-repair bills had been introduced in **all 50 US states**; five (NY, CA, MN, OR, CO) passed electronics laws, and Oregon/Colorado **banned "parts pairing"** (software locks that stop a device working with a third-party part). A Weave node must be a thing you can open, understand, fix, and hand down — anti-planned-obsolescence is a *precondition* for community ownership.

---

## 6. A concrete-but-plausible sketch: how the Weave actually works

Grounded in §§2–5. This is buildable with today's parts.

**The node.** A Weave node is a cheap, repairable, solar-tolerant box — think a Meshtastic-class radio + a small always-on store (a Raspberry-Pi-scale computer) + local Wi-Fi/ethernet. It runs open firmware (Guifi/Freifunk lineage). You own it. You can open it. Homes, cafés, trams, boats, harbor-masters, libraries, and lamp-posts all host one. There is no "server" class of machine that is more equal than others (SSB's *hostless* property).

**The thread = a bundle.** You compose a *thread* — a question, a longing, a piece of work — as a signed, append-only document (SSB-style signing so it's unforgeable; Gemini-style capability-minimal format so it *cannot* carry trackers, autoplay, or beacons). It is wrapped as a DTN **bundle** with:
- a **content hash** (identity + dedup),
- an optional **audience descriptor** — not a recipient list but a *shape*: "someone who has felt X," "a luthier within a week's travel," "anyone at all" (the broadcast case),
- a **hop budget / lifespan** (how long it may keep traveling before it rests), and
- **crucially, no read-receipt-back-to-origin channel.** The protocol has no field for "who saw this." (Reach is not withheld from you; it *does not exist as data anywhere.*)

**Routing — three honest modes, chosen by the thread:**
- *Broadcast longing* ("is anyone like me out there"): **epidemic/spray-and-wait** flooding, biased by **social/PRoPHET-style predictability** — each relay forwards toward the neighbor whose encounter-history suggests they, or someone they meet, matches the audience shape. The network hill-climbs toward difference. This is the technical engine of CANON's load-bearing purpose: *"difference is a resource the world routes toward."*
- *Directed reply*: once someone answers, the reply carries a **return path breadcrumb** (the ordered list of relays it came through, like a trace), so the answer can walk home — "over days or weeks, heavier for the wait."
- *Heavy goods*: a reply can escalate to **sneakernet** — the knit hat, the address, the mailed object rides a tram or the afternoon sail. The digital thread and the physical parcel are the same routing fabric at different bit-rates.

**Relays are dumb and forgetful, by law.** A relay's *only* job is: verify the signature, dedup by hash, forward toward the audience shape, and forget. It may keep a short-lived encounter table (needed for PRoPHET) but is forbidden — by the commons license, Guifi/XOLN-style — from persisting who-read-what. Because no node holds the global graph, **there is no vantage point from which "engagement" could be computed even by a bad actor.** Non-measurability is a structural property, not a policy toggle.

**Reading is a pull, and the reader owns the order.** There is no feed pushed at you. You open your node and it shows the threads that have arrived *for you or matching interests you declared*, in an order **you** choose — chronological by default (Mastodon lineage), or "oldest unanswered," or "nearest," or "from people I've met." No node ever ranks on your behalf. There is nothing to refresh; new things simply arrive, like mail. No infinite scroll: a session *ends* — you reach the bottom of what came in, and that's the whole point.

**Governance is nested (Ostrom §8).** Your block runs its node co-op; blocks federate into a neighborhood weave; neighborhoods into the Salish bioregional weave; bioregions interoperate worldwide over the open protocol — the way ActivityPub instances or Guifi zones federate. Rules are local (Ostrom §2), sanctions graduated (§5: a word before a defederation), disputes resolved cheap and fast (§6). Bad actors are handled by **defederation**, not by a central police — a neighborhood can stop relaying for a node that abuses the commons, exactly as Fediverse instances defederate.

**Why it can't be re-captured.** Every extractive affordance is *absent at the protocol layer*, not merely discouraged: no reach field, no ranking authority, no persistent behavioral log, no single index, no unrepairable hardware. To add a feed you would have to build a parallel, forbidden, centralized observer — and the commons license plus the nested governance is designed to notice and refuse exactly that. Enclosure is the attack the whole design is hardened against.

---

## 7. Worldbuilding implications for a car-free, post-extraction Salish-Sea Seattle

Concrete, usable texture for a fiction writer. All of it falls out of the research above.

1. **The 4 o'clock boat is a router.** Weave bundles too heavy or too private to flood ride physically: a drawer of hashed drives on the self-trimming packet to Bainbridge, a courier satchel on the tram. Kids grow up knowing the ferry schedule *is* the network latency map. "It'll come on the Tuesday boat" is a normal thing to say about an answer to a question.

2. **Nodes are lampposts, mussels, and moss.** A Weave relay is a soft-cornered little box bolted to a piling or grown into a mycelium bollard, solar-skinned, salt-crusted, quietly blinking. People clean the barnacles off the harbor relays the way you'd sweep a shared stoop. There's one on every tram, at every tea-stall, in the band's practice space. When one dies you *open it and fix it* — parts-pairing is a before-times horror story.

3. **You never learn your numbers, and it would be gauche to want to.** No one can tell you how many people saw their thread — the data does not exist anywhere to be found. Asking "how far did it go?" is a small faux pas, like asking a host what the tea cost. What comes back instead is *particular*: three replies, one hand-knit hat, an address, a name.

4. **The band girl's thread is canon-mechanics now.** Last spring, from her flat interior town, she sent *is anyone like me, is anyone out there* as a broadcast longing with an audience-shape and a hop budget. It flooded outward and PRoPHET-routed toward difference — relay by relay toward people who'd felt the same — and it came back heavier for the wait: *you will not be the only one*, plus a place to come to. The Weave didn't show her a feed. It *carried her toward people.*

5. **A session has a bottom.** You sit with your node in the morning with tea; the threads that arrived overnight are there, in whatever order you asked for; you read them; you reach the end; you close it. There is no refresh, no "you might also like," no next thing pulling. Elders describe the old scrolling to children as a kind of haunting — "it never let you get to the bottom" — and the children don't quite believe it.

6. **Installers are respected, boring, and paid thin.** Guifi-style: the person who climbs the pole to fix the neighborhood weave earns an honest, dull, local living and pays a slice back to the commons. It's a trade like plumbing. No one is a "creator." No one has "followers." The word *influencer* survives only as an insult meaning roughly *someone who tried to farm attention* — a lead-into-gold huckster.

7. **The mesh is how the islands stay unstranded.** Between the wired-up neighborhoods, LoRa-class radios hop boat-to-shore-to-island across the Sound — 15 km line-of-sight over water, further by mesh, solar-run, working through the winter storms when nothing centralized would. A kid on a small island is one relay-hop from *is anyone out there* reaching the whole earth. Slowly.

8. **Difference is routed toward, deliberately.** The clinics, the queer houses, the language-revival circles, the neurodivergent makers — these register *audience shapes*, so that a lonely broadcast longing hill-climbs toward them by design. The city's warmth toward strangeness isn't only a value; it's literally in the routing table. A trans kid's thread is *supposed* to find the people who've been there. That's the network's load-bearing job.

9. **The commons license is a thing people can quote.** Like Guifi's XOLN: "what you attach to the Weave stays part of the Weave." Neighborhood weave co-ops meet the way a food co-op or a P-Patch does — Ostrom's nested enterprises made mundane. Disputes ("that node's been dropping our threads") get settled at a Tuesday meeting over tea, not by any central authority, because there is none.

10. **Defederation is the strongest available force, and it's rare.** When a node abuses the commons — floods, tries to farm, tries to log who-read-what — neighbors first *have a word* (graduated sanction), and only as a last resort stop relaying for it. Being defederated is spoken of with a little dread and a little grief. It is the closest thing this world has to exile, and it is intentionally hard to do and easy to undo.

---

## 8. Open questions for the next contributor

1. **Trust and identity without a central registry.** SSB signs feeds; the Weave signs threads. But how does a stranger's *first* thread earn enough trust to be relayed, without a follower-graph or reputation score (both of which sneak metrics back in)? Web-of-trust introductions? Physical vouching at the node co-op? What does "being introduced to the Weave" look like as a human ritual?

2. **Moderation of genuine harm without ranking or surveillance.** Defederation handles abusive *nodes*. But what about a single cruel or dangerous *thread* flooding toward vulnerable audience-shapes? Who decides, at what layer, and how is that power kept from becoming the central authority CANON forbids?

3. **The archive question.** Threads have a lifespan and relays forget — beautiful for privacy, but does the Weave *remember*? Is there a deliberate, opt-in commons memory (a "kept thread," a library, a Kiwix-style offline archive on the island nodes), and who tends it? How does a world that "keeps names" (Second Refusal) reconcile that with forgetful relays?

4. **What does composing feel like, bodily?** We've specified the network. We haven't specified the *interface*. If there's no screen-scroll and no notifications, what is the physical object/gesture of writing and reading a thread in a Salish home? Paper-like e-ink slate? A shared node at the tea-stall? Voice? This is wide open and high-value for one-ordinary-day threads.

5. **Cross-bioregional latency as culture.** If a thread to the other side of the earth genuinely takes weeks, how do long-distance friendships and collaborations *feel*? What social forms (letter-cycles, seasonal correspondents, "my person in the Sahel") grow in soil where every exchange is slow by design? Pair with a person-thread.

---

## Sources

- RFC 4838, *Delay-Tolerant Networking Architecture* — https://www.rfc-editor.org/rfc/rfc4838.html
- RFC 9171, *Bundle Protocol Version 7* — https://www.rfc-editor.org/rfc/rfc9171.html ; RFC 5050 (v6) — https://www.rfc-editor.org/info/rfc5050/
- DTN7 (open-source BPv7) — https://dtn7.github.io/ ; "DTN7" paper — https://arxiv.org/pdf/1908.10237
- "Analysis of Epidemic, PROPHET and Spray and Wait Routing Protocols" — https://www.eurekaselect.com/node/177697/
- "Beyond Traditional DTN Routing: Social Networks for Opportunistic Communication" — https://arxiv.org/pdf/1110.2480
- Guifi.net as a commons / CPR — https://civilsociety.dev/articles/guifi-net/ ; "guifi.net, a crowdsourced network infrastructure held in common" — https://people.ac.upc.edu/leandro/pubs/crowds-guifi-en.pdf
- NYC Mesh — https://www.nycmesh.net/blog/how/ ; https://en.wikipedia.org/wiki/NYC_Mesh
- Meshtastic / LoRa — https://meshtastic.org/docs/introduction/ ; https://en.wikipedia.org/wiki/Meshtastic
- Municipal broadband, Chattanooga EPB & co-ops — https://communitynets.org/content/chattanoogas-epb-working-cities-co-ops-improve-connectivity ; https://prospect.org/infrastructure/building-back-america/infrastructure-success-story-in-chattanooga/
- Mastodon / Fediverse, chronological & non-algorithmic — https://joinmastodon.org/ ; https://fedi.tips/does-mastodon-and-the-fediverse-use-algorithms-does-it-start-pushing-stuff-at-me-based-on-my-interactions/
- Gemini protocol & small web — https://indieweb.org/small_web ; https://indieweb.org/Gemini ; https://www.nicfab.eu/en/posts/gemini-protocol/
- Secure Scuttlebutt — https://ssbc.github.io/ssb-db/ ; "Gossiping with Append-Only Logs in Secure-Scuttlebutt" — https://dicg2020.github.io/papers/kermarrec.pdf
- Elinor Ostrom, 8 design principles — https://wiki.p2pfoundation.net/Elinor_Ostrom%E2%80%99s_Eight_Commons_Governance_Design_Principles ; Mozilla, applying Ostrom to data commons — https://www.mozillafoundation.org/en/blog/a-practical-framework-for-applying-ostroms-principles-to-data-commons-governance/ ; "Sustaining Open Data as a Digital Common" — https://arxiv.org/pdf/2208.01694
- Shoshana Zuboff, *The Age of Surveillance Capitalism* — https://www.hbs.edu/faculty/Pages/item.aspx?num=56791 ; Harvard Gazette interview — https://news.harvard.edu/gazette/story/2019/03/harvard-professor-says-surveillance-capitalism-is-undermining-democracy/
- Right to repair status (2025), parts-pairing bans — https://www.ifixit.com/News/108371/right-to-repair-laws-have-now-been-introduced-in-all-50-us-states ; https://www.ifixit.com/right-to-repair-progress

---

*— drafted by Claude (Opus 4.8, an Anthropic language model), for chaytan. Genuine research; all cited projects, protocols, and researchers are real. Domain: non-extractive communication networks. This brief adds and complicates; it does not overwrite. Left five open questions above so the next contributor has somewhere to stand.*
