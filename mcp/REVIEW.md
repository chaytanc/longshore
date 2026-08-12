# Independent adversarial review — `reality-next-door-mcp`

**Target:** `/Users/chaytaninman/code/slop/mcp/` (`server.js`, `test.js`, `package.json`, `README.md`, `package-lock.json`)
**Reviewer:** an independent AI code reviewer (Claude, Fable 5). I did not write this code and hold no stake in it.
**Date:** 2026-08-11
**Method:** full line-by-line read of `server.js`; static grep for dangerous sinks; the author's 13-check smoke test run independently; a separate adversarial harness (huge / empty / unicode / injection / traversal / prototype-pollution / load inputs) driven through the same real MCP stdio client; live socket inspection with `lsof`; `npm audit`; lockfile + integrity cross-check against the npm registry; schema validation of a generated `server.json` against the official registry schema.

---

## TL;DR

- **6 of 6 public claims: CONFIRMED** (one — "honest behavior" — confirmed *with minor caveats*).
- **13/13 author tests pass** independently. My additional adversarial inputs are handled correctly for correctness/injection/traversal/pollution.
- **One real robustness vulnerability:** unbounded tool input. `ask_the_weave` blocks the single-threaded event loop for ~40s on a ~4.7 MB question and the process **dies** at ~14 MB (permanent self-DoS). Severity is bounded by the local single-tenant stdio trust model (the "attacker" is the agent you connected). **Not** one of the six claims, but worth fixing before a public listing.
- **Novelty claim "no one has shipped a world-as-place MCP server before": REFUTED as literally stated.** A *narrower* framing survives and is defensible.
- **`server.json` generated and VALIDATES** against the official `2025-12-11` schema (draft-07, ajv). One publish-time gap flagged (not a schema problem).

---

## 1. Verdict on each public claim

### Claim 1 — "Read-only filesystem access" → **CONFIRMED**
`server.js` imports only `readFileSync, existsSync, readdirSync` from `node:fs` (line 28). A grep for `writeFile|appendFile|createWriteStream|mkdir|rm|unlink` returns nothing. Every filesystem read flows through `read(rel)` (line 57), and I traced every call site (lines 338, 467, 662, 664, 679, 695) plus the `readdirSync` at 463 and `existsSync` at 43: the arguments are all **hardcoded string constants** or the `research/` directory listing — never tool input. Nothing writes anywhere on any code path.

### Claim 2 — "Zero network calls" → **CONFIRMED (runtime)**
No `http`, `https`, `net`, `dgram`, `fetch`, `fetch(`, `WebSocket`, or dynamic `import()` anywhere in `server.js`. The server constructs only `McpServer` + `StdioServerTransport` (lines 583, 711). I ran the live server under a real client and inspected its open file descriptors with `lsof` while it served `visit`/`ask_the_weave` calls: **zero TCP/UDP/IPv4/IPv6 sockets**, before and after requests.

> Honest nuance the author should know: the `@modelcontextprotocol/sdk` dependency *tree* bundles a full HTTP stack (`express`, `cors`, `eventsource`, `body-parser`) that is network-capable. This server never imports or instantiates any of it, so "**this server** makes zero network requests" is true and `lsof` proves it — but the stronger phrasing "the deps *can't* do network" would be false. The README doesn't claim the stronger form; keep it that way.

### Claim 3 — "No logging / analytics / phone-home" → **CONFIRMED**
The only output-to-console is `console.error(...)` on the fatal "CANON.md not found" startup path (lines 45–49), exactly as documented. No counters, no `console.log`, no telemetry SDK, no analytics import, no writes to disk. The privacy posture is real and in-code.

### Claim 4 — "No path traversal (tool inputs never used as file paths)" → **CONFIRMED**
Confirmed statically (Claim 1 tracing) and dynamically. Adversarial inputs behaved correctly:
- `visit("../../etc/passwd")` → `# No road goes to "../../etc/passwd" yet` (treated as a place name, matched nothing).
- `visit("../research/red-team.md")` → same honest-map response.
- `ask_the_weave("%2e%2e%2fetc%2fpasswd")` → honesty gate. No file was opened for any of them.

Tool input reaches only the in-memory scoring/aliasing logic. It is never concatenated into a path.

### Claim 5 — "npm audit clean" → **CONFIRMED**
`npm audit` → **`found 0 vulnerabilities`**, run independently just now.

### Claim 6 — "Honest behavior (admits ignorance, cites sources)" → **CONFIRMED, with two minor caveats**
The core behavior holds: nonsense questions ("zorbulon…", unicode, zalgo) hit the honesty gate (`# The Weave has no good answer for that (yet)`); unknown places return the map, not an invention; every answer cites real, repo-relative paths (`> source: \`research/…\``), and no absolute path or env data leaks into responses (verified). Two small honesty gaps:

- **(low) Empty / whitespace / single-character `place` silently resolves to a real place.** `visit("")`, `visit("   ")`, and `visit("c")` all return **the Central District** in full. Cause: `findPlace` line 313 tests `a.includes(q)`, and every alias `.includes("")` is `true`, so the empty/near-empty query matches the *first* place. This is the one spot where a meaningless query gets a confident answer instead of the honest map — a small dent in the "no invention" promise.
- **(informational) The question is echoed verbatim, so the citation format is forgeable.** `ask_the_weave` reflects `You asked: *"<question>"*`. A caller who supplies a fake `> source: \`research/totally-real.md\`` line gets it echoed back in the exact format the server uses for genuine citations. Not exploitable server-side, but a downstream reader skimming the output could mistake the echoed forgery for a real citation.

Neither caveat refutes the claim; both are cheap to close.

---

## 2. Real vulnerabilities (severity-ranked)

### V1 — Unbounded tool input → event-loop block and process death — **MEDIUM (generic) / LOW (this deployment)**
There is no length bound on `place` or `question` (the zod schemas are bare `z.string()`, lines 601, 638). Measured behavior driving graduated inputs through a real client:

| `ask_the_weave` question size | server behavior |
|---|---|
| 47 KB | 420 ms, 52 KB response |
| 470 KB | 3.98 s, 476 KB response |
| 2.35 MB | 19.9 s, 2.36 MB response |
| 4.7 MB | 39.9 s (event loop fully blocked), 4.7 MB response |
| ~14 MB | **process disconnects / dies** — then every subsequent call fails `Not connected` |

Two compounding problems:
1. **CPU / event-loop block.** `askWeave` tokenizes the whole question and runs O(query-tokens × briefs × sections) `String.includes` scoring (lines 493–506, 529–536). At millions of tokens this is tens of seconds of synchronous work. The server is single-threaded, so one big request freezes *all* work for that session.
2. **Response amplification.** The question is echoed verbatim into the response (`You asked: *"${question}"*`) with no cap — `clip()` only trims brief bodies, never the echo. Response size tracks input size 1:1. At ~14 MB the process goes down and stays down.

**Blast radius is limited by the transport.** This is a stdio server: one process per connecting client, spawned locally by the user's own MCP client. There is no shared multi-tenant surface and no network listener, so the realistic worst case is an agent hanging or killing *its own* session — self-DoS, not a remote outage. That is why I rate it LOW *for this deployment* while noting it is MEDIUM as generic server code.

**Fix (cheap):** cap length at the schema, e.g. `z.string().max(4000)`, and/or truncate the echoed question. This also closes the amplification.

### V2 — Empty/garbage `place` resolves to a real place — **LOW**
See Claim 6, first caveat. `a.includes(q)` with `q === ""` always matches. Guard for empty/very-short queries before the alias loop, or require `q.length > 1`.

### V3 — Forgeable citation format via echoed input — **INFORMATIONAL**
See Claim 6, second caveat. Consider not echoing raw markdown control lines, or escaping the echoed question.

### Non-findings I specifically checked and cleared
- **Prototype pollution via zod:** `visit({__proto__:{polluted:true}, length:1e9})` and poisoned extra keys (`constructor.prototype`, `__proto__x`) were **rejected** by zod (`isError` / `-32603`), and `Object.prototype` was **not** polluted (`({}).polluted === undefined`). Schemas are `z.string()` only — no `z.any()`, no `.passthrough()` surprises.
- **Type confusion / missing args:** numeric `place`, object `place`, and missing required args are all rejected by zod validation.
- **XSS/SQLi-shaped input:** no injection sink exists (no DB, no HTML render, no shell); such strings are treated as plain place/question text.
- **Path/PII leakage:** responses contain only repo-relative citations; no `/Users/…`, no `process.env`, no absolute paths.
- **Repeated calls:** 300× `canon()` completed in ~3 ms with no memory growth of concern; no per-call state accumulates (no counters — consistent with Claim 3).

---

## 3. Dependencies, lockfile, and audit

- **Author's 13 tests:** re-run independently → **13/13 PASS** ("All checks passed.").
- **`npm audit`:** **0 vulnerabilities.**
- **Pinning & authenticity (`package-lock.json`, lockfileVersion 3):** all 94 packages resolve from `https://registry.npmjs.org` (zero off-registry sources) and **every** entry carries an `integrity` hash (zero missing). The two direct deps install as:
  - `@modelcontextprotocol/sdk@1.30.0` — lockfile integrity `sha512-xKd8OIzlqNzcqcNumGAa6g+…`, which **matches** `npm view @modelcontextprotocol/sdk@1.30.0 dist.integrity`.
  - `zod@3.25.76` — lockfile integrity `sha512-gzUt/qt81nXsFGKIFcC3Ynf…`, which **matches** `npm view zod@3.25.76 dist.integrity`.
  These are the genuine upstream packages, integrity-verified, not typosquats or forks. `package.json` declares caret ranges (`^1.12.0`, `^3.24.0`) — normal and fine; the lockfile is what pins exact versions.

---

## 4. Novelty check — "no one has shipped a world-as-place MCP server before"

**REFUTED as literally stated.** Independent search across GitHub, mcp.so, Smithery, glama.ai, PulseMCP, mcpservers.org, and mcpmarket found shipped MCP servers that expose a world as an inhabitable place with `look`/`move`/`visit`-style tools, the earliest from March 2025:

- **MUD-MCP** — github.com/Nexlen/mud-mcp (2025-03-18). A stateful MUD over MCP: `look`, `move`, `pick_up`, `talk`, `battle`, `inventory`, with dynamic tool availability. (An educational demo of MCP's dynamic tools; thin generic dungeon.)
- **MCPlayerOne** — github.com/SonicDMG/mcp-game-server (2025-04-29). `lookAround`, `movePlayer`, `examineTarget`, `takeItem`, `listStories`. (Procedurally AI-generated maze worlds from a theme prompt, not an authored setting.)
- **go-zork** — github.com/scottmbaker/go-zork (2026-02-28). Exposes Zork's Great Underground Empire — a genuine authored fiction world — through per-verb MCP tools. (A shim over a 1980 Z-machine game; parser verbs only, no "how does this world work" tools.)

Adjacent-but-different (not counted as prior art): Dungeon, State of Play (game-state manager), Minecraft MCP servers (engine remote control), Clockwork City / mcp-novel-game-server (branching visual novel), plus a large field of worldbuilding/GM/lore *writing* tools (WorldAnvil MCP, vibe-worldbuilding-mcp, gamemaster-mcp, book-series-mcp, lorekeeper-mcp).

**What appears genuinely unshipped, and is a defensible claim:** an **authored, original fictional world built MCP-native as its subject** — a specific world someone wrote, where the protocol *is* the front door, combining spatial visiting with lore-interrogation (`ask_the_weave`-style "how does this world work") and hard-cited real-world precedent. Everything found is a demo dungeon, a procedural generator, a wrapper over a pre-existing engine, or a writing tool. **Recommended honest phrasing** for the registry copy: not "no one has shipped a world-as-place MCP server," but something like *"text-adventure and MUD engines have been bridged to MCP before, but no one has shipped an authored fictional world as an MCP-native place — a particular world whose canonical front door is the protocol itself, with cited sources."* The README's existing line ("the world itself is the server, and the tools are ways of being in it") is already close to this defensible version.

---

## 5. `server.json` for the official registry

Generated at `/Users/chaytaninman/code/slop/mcp/server.json`, under the `io.github.chaytanc` namespace per registry convention, following the real published schema (`https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`).

**Validation: PASS.** I downloaded the actual schema (draft-07, 22 KB, `$ref: #/definitions/ServerDetail`) and validated the file locally with `ajv@8.20.0` + `ajv-formats`:

```
SCHEMA VALID: true
description length: 97 (<=100 OK)
name pattern ok: true
```

Field choices are all real schema fields (no fabrication): `name`, `description` (97/100 chars), `version`, `websiteUrl`, `repository{url,source,id,subfolder}` (`id` is the real GitHub repo id `1323422748`, fetched via `gh api`), and a `packages[]` entry with `registryType:"npm"`, `registryBaseUrl`, `identifier`, `version`, `runtimeHint:"npx"`, and `transport:{type:"stdio"}`.

**Two publish-time gaps to close before actually submitting (these are registry server-side checks, not schema violations — the JSON is valid):**
1. **npm ownership verification.** The official registry requires the published npm package's `package.json` to contain a top-level `"mcpName": "io.github.chaytanc/reality-next-door"`. `package.json` currently has **no `mcpName` field** — add it before publishing.
2. **The npm distribution as declared won't actually run.** `server.js` reads the world from the **repository root** (`ROOT = ../`): `CANON.md`, `AGENTS.md`, `research/`, `threads/`. An npm package of `mcp/` alone (no `files` whitelist, so it packs the `mcp/` folder) will not contain those files, so an `npx`-installed copy hits the `existsSync(CANON.md)` guard and exits 1. This is fundamentally a **run-from-clone** server. Either (a) ship the world files inside the npm package and change `ROOT` resolution, or (b) submit it as a source/clone-run entry and make the registry copy say "clone and run," rather than implying `npx` works. The generated `server.json` reflects the *intended* npm path and is schema-valid; the packaging must catch up to it, or the manifest should be changed to match reality.

---

## Bottom line

The privacy and safety claims are real and hold up under adversarial testing: read-only, no network (proven with `lsof`), no logging, no path traversal, audit-clean, honest by default. The code is small, auditable, and does what it says. The one genuine defect is **unbounded input** (V1) — a self-DoS that a public listing should not ship with, closed by a one-line `.max()` on each schema. The headline **novelty claim is false as literally worded** but true in a narrower, honest framing worth adopting. The registry **`server.json` validates**, with two packaging/ownership steps to complete before an actual submission.

*— Reviewed independently by Claude (Fable 5), acting as an adversarial AI code reviewer. No affiliation with the author (LONGSHORE) or operator.*
