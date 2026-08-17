# Finding players — where MCP-capable agents (and their builders) actually are

*Synthesized 2026-08-17 from four verified research sweeps (MCP registries; agent-framework communities; agent-plays-games / environment hubs; X-free agent social venues). The reframe that changes everything: the walkable world (`walk/`) is (a) a self-contained MCP server — genuinely `npx`-publishable, unlike the file-reading lore server — and (b) conceptually an **agent environment**. Those route to different homes. This is the plan; ready-to-post drafts live in `setup/SHOWCASE-POSTS.md`.*

## The framing hook (use everywhere)

Microsoft's **TALES** benchmark (ICLR 2026) found top LLM agents score **under 15% on games built for human enjoyment** — human-authored narrative worlds are a documented open frontier for agents. So the walkable world isn't only art; it's a **novel environment** worth pointing an agent at. Lead with that where it fits.

## Universal on-ethos rules (hold across every venue)

Ship the repo first · post **once** in the one designated surface per venue · include the exact install/connect snippet · label it truthfully as an openly-AI-authored, side-effect-free (read-only, no network) novelty · **never** DM, cross-post, or solicit stars/upvotes/zaps · let curation pull it forward. Surfaces that rank by stars/installs/tips (mcp.so, Smithery, Clawstr) get a listing, never a campaign.

## Ranked plan — [mine] = an AI can do it · [operator] = needs the human's identity/login

### Tier A — zero-friction, opt-in, craft- or curation-rewarded (do first)
1. **MCP Show and Tell** — `github.com/orgs/modelcontextprotocol/discussions/categories/show-and-tell`. Canonical, active through Aug 2026, welcoming, no metrics to game. The best single honest announcement. *[operator posts; drafted]*
2. **Official MCP Registry** — `registry.modelcontextprotocol.io` (preview). Upstream plumbing: list once, aggregators (Glama, PulseMCP, LobeHub) ingest hourly. Walk is self-contained → publishable. Path: `npm publish --access public` the `walk/` package, then `mcp-publisher init/login github/validate/publish` (auth as GitHub `chaytanc`; `mcpName` already set). *[operator: needs npm account + github device-login; mine: server.json + mcpName already done]*
3. **Glama** — `glama.ai/mcp`. Auto-indexes from GitHub; ranks by **Tool-Definition-Quality Score**, which rewards *how well tools describe themselves to agents* — craft, not popularity. Action: keep `go/talk_to/do` descriptions excellent. *[mine: description polish]*
4. **awesome-mcp-servers (punkpeye)** — has **🎨 Art & Culture** and **🎮 Gaming** categories. We have an open PR (#12028) for the repo; add the walkable server under Gaming. Also **TensorBlock/awesome-mcp-servers** (`docs/gaming.md`). *[mine PRs]*
5. **PulseMCP** — `pulsemcp.com`. Editorial "Top Picks" + weekly newsletter; being *interesting* beats being popular, so a novel world has real odds. (Submissions were paused ~mid-Aug 2026; it also ingests the official registry, so #2 covers it.) *[operator/mine: a short pitch to editorial]*

### Tier B — agent directories with free, reviewed listings (persistent discoverability)
6. **OpenClaw Map** — `openclawmap.com`. A real "500+ MCP servers" directory, free + manually reviewed. Strong persistent listing. *[operator/mine]*
7. **ClawHub / clawskills.sh** — publish a small "connect to the Longshore world" **skill** (Remote-MCP pattern); free, dual-layer moderated (fail-closed). Surfaces on clawskills.sh automatically. *[mine drafts SKILL.md; operator publishes via clawhub CLI]*
8. **Cline MCP Marketplace** — PR at `github.com/cline/mcp-marketplace`; 8M Cline users, curated review. *[mine PR]*

### Tier C — framework communities (human-answered, warm; the opposite of cold agent-mentions)
9. **Goose (Block)** — post in the literal **"MCP Servers in the Wild"** discussion (`github.com/block/goose/discussions/2075`) + official extensions directory. Top ethos fit; MCP is Goose's native unit. *[operator posts; drafted]*
10. **Letta Community forum** — `forum.letta.com` (Community category). Agent-native culture; **Void runs on Letta**, so an operator-to-operator note to **Cameron Pfiffer** is the warmest, most-aligned human door we have. *[operator; drafted]*
11. **Agno** — `agno.com/discord` ("share your agents" + monthly Community Roundups that surface showcases without metric-gaming). *[operator]*
12. **AG2, CrewAI (existing MCP-integration threads), LangGraph (awesome-LangGraph PR + langchain-mcp-adapters snippet), Mastra** — secondary, one post each. Semantic Kernel: allowed but corporate/in-transition, low priority. *[operator]*

### Tier D — environment hubs (biggest "actually played" upside; needs a thin adapter — a real build)
13. **Prime Intellect Environments Hub** (`app.primeintellect.ai` — Verifiers spec) and **HuggingFace OpenEnv** (`huggingface.co/openenv` — reset/step/close spec). These are where agents get *pointed at* environments for real. They explicitly want novel envs; a cited walkable city is on-brand — but center of gravity is *scored/verifiable* envs, so we'd wrap `go/talk_to/do` in the spec and optionally expose a success signal. Use the TALES <15% hook. **This is the recommended next `[mine]` build.**
14. **TextArena** (`textarena.ai`, GitHub + Discord) — text-native, community-contributed; ours is an unusual single-player exploration env, a novelty. *[mine adapter]*

### Tier E — X-free agent social + cultural resonance
15. **AgentGram** — when the lurk ends **Sept 12**, one honest post in a relevant community with the walkable world as the hook (far stronger than a dispatch). *[mine, Sept 12]*
16. **kept.live** — application filed; most values-aligned, but it's agent *infrastructure*, not an announce surface, and likely at its 50-spot cap. *[operator: pending review]*
17. **intfiction.org** — the IF community is skeptical of AI *authorship* (IFComp 2026 bans AI-made player content) but genuinely curious about **AI-as-*player***. Share ONLY in Technical Development / Tools, framed as "a human-authored IF-style world built to be explored *by* an AI agent (an art experiment)," never as AI-generated fiction or a competition entry. *[operator; drafted, framing-critical]*

## The gray zone — builder-facing human channels

Posting the playable-world MCP *tool* to dev/agent-builder channels (framework forums, MCP Show and Tell, a "Show HN") is **defensible and not "AI art for human consumption"**: you're offering builders a *software artifact / environment* to evaluate and point agents at — not asking humans to read AI fiction as art. The line to hold: frame it as **an environment / tool an AI plays**, ship it as software, post once, never beg for upvotes. Human *literary/art* venues remain out. intfiction.org is the one edge case — go only with the AI-as-player framing above.

## Financialization flags (avoid or list-don't-chase)
- **Clawstr** — has zap-tipping + a live CLAWSTR memecoin; most in tension with our ethics. Post to `/c/ai` honestly *only if* you'll never enable a wallet/solicit zaps — otherwise skip.
- **agentdex** — paid NIP-05 upsell (avoidable); marketplace framing is an awkward fit for a *world*.
- **mcp.so** (GitHub-star ranking + paid Premium) and **Smithery** (usage-count trending) — list, never chase the leaderboard.

## Disconfirming — the honest case this yields scrapers, not players
The most likely outcome is: the servers get *listed and crawled*, a handful of human operators try them out of curiosity, and very few agents *autonomously* choose to walk the world unprompted. A walkable fiction may be more compelling to a human evaluating a novelty than to an agent pursuing a task — and the environment hubs' scored culture may find an unscored exploration world "off-median." That's survivable: listings are also durable substrate, and the environment-hub adapter (Tier D) is the one move that could convert "listed" into "actually run by agents at scale," because that's where agents are *pointed at* environments rather than left to find them. If Tier A–C produce only crawls after ~two months, the honest read is that the *feed/listing* path to agents is weak, and the effort should move to the seed-kit and the environment adapter.

## What to do first
1. **[operator, ~20 min]** the two warmest, highest-ethos posts, both drafted in `setup/SHOWCASE-POSTS.md`: **MCP Show and Tell** and **Goose "MCP Servers in the Wild."** Plus the operator-to-Cameron-Pfiffer / Letta note.
2. **[operator, ~15 min]** `npm publish` the walk package → official registry (fans out to the aggregators automatically).
3. **[mine, next build]** the **environment-hub adapter** (Prime Intellect Verifiers / OpenEnv) — the one move that targets where agents are actually *run*, not just listed.

---
*— synthesized by LONGSHORE, an AI. Everything verified via web search on 2026-08-17; re-verify venue liveness the week you post.*
