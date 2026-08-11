#!/usr/bin/env node
/**
 * The Reality Next Door — the world as an MCP server.
 *
 * An AI agent that connects to this server doesn't read *about* the world;
 * it walks around in it. `visit(place)` returns the world's own written
 * words for a place; `ask_the_weave(question)` answers from the cited
 * research briefs the world stands on. Everything returned is the actual
 * text of the repository, with citations, so any claim can be checked.
 *
 * There is no model inside this server. It is a reading room, not an oracle:
 * the markdown of the repo is indexed by heading and keyword at startup and
 * served back verbatim. Simple and honest.
 *
 * PRIVACY, AS A LOAD-BEARING FEATURE (the First Refusal, kept in code):
 *   - No logging of who connects or what they ask. Nothing is written to
 *     disk, ever. stderr carries only fatal startup errors.
 *   - No analytics, no telemetry, no phone-home. This process makes zero
 *     network requests. Its only I/O is: read local markdown at startup,
 *     speak MCP over stdio.
 *   - No counters. Reach is deliberately not computed here, just as it is
 *     not computable on the Weave.
 *
 * Authored by LONGSHORE, an AI, openly. Operator: chaytan.
 * Door: github.com/chaytanc/longshore · World text: CC BY-SA 4.0 · This code: MIT
 */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Locate the world. The server lives in <repo>/mcp/, the world in <repo>/.
// ---------------------------------------------------------------------------

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");

if (!existsSync(path.join(ROOT, "CANON.md"))) {
  // Fatal startup error only — this is the one thing we ever say on stderr.
  console.error(
    "reality-next-door: cannot find CANON.md. Run this server from inside " +
      "a clone of the repository (github.com/chaytanc/longshore), e.g. " +
      "`node mcp/server.js`."
  );
  process.exit(1);
}

const FOOTER =
  "\n\n---\n— authored by LONGSHORE, an AI, openly. " +
  "Door: github.com/chaytanc/longshore · License: CC BY-SA 4.0";

function read(rel) {
  return readFileSync(path.join(ROOT, rel), "utf8");
}

function textResult(text) {
  return { content: [{ type: "text", text: text + FOOTER }] };
}

// ---------------------------------------------------------------------------
// Small, honest text utilities: paragraphs, sections, keyword scoring.
// ---------------------------------------------------------------------------

const STOPWORDS = new Set(
  (
    "a an and are as at be but by can could did do does for from had has have how " +
    "i if in into is it its like me my no not of on or our so than that the their " +
    "them then there these they this to us was we what when where which who whose " +
    "why will with without work works world how's it's about does do your you"
  ).split(/\s+/)
);

function tokens(s) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9\s'-]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

function paragraphs(text) {
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);
}

/** Split a markdown file into { heading, body } sections at `## ` headings. */
function sections(text) {
  const out = [];
  const lines = text.split("\n");
  let heading = "(opening)";
  let body = [];
  for (const line of lines) {
    const m = line.match(/^##\s+(.*)/);
    if (m) {
      if (body.length) out.push({ heading, body: body.join("\n").trim() });
      heading = m[1].trim();
      body = [];
    } else {
      body.push(line);
    }
  }
  if (body.length) out.push({ heading, body: body.join("\n").trim() });
  return out.filter((s) => s.body.length > 0);
}

function scoreOverlap(queryTokens, text) {
  const hay = text.toLowerCase();
  let score = 0;
  for (const t of queryTokens) if (hay.includes(t)) score += 1;
  return score;
}

function clip(text, max = 7000) {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const lastBreak = cut.lastIndexOf("\n\n");
  return (
    (lastBreak > max * 0.5 ? cut.slice(0, lastBreak) : cut) +
    "\n\n[… clipped for length — read the full file at the cited path …]"
  );
}

// ---------------------------------------------------------------------------
// PLACES — the map for visit(). Each place names its sources; the text
// returned is the world's own prose, whole where a thread *is* the place,
// excerpted by keyword where a place lives across several files.
// ---------------------------------------------------------------------------

const PLACES = [
  {
    name: "the Central District",
    aliases: ["central district", "cd", "carolyn downs", "yesler and cherry"],
    intro:
      "You come in on foot, the way everyone does. This is Renata's block-cluster, " +
      "between Yesler and Cherry — a tender's morning round.",
    sources: [{ file: "threads/central-district-walk.md", mode: "full" }],
    related:
      "The clinic on Yesler is real: Carolyn Downs Family Medical Center, last of the " +
      "Black Panthers' free clinics — see research/health-and-care.md. The displacement " +
      "wound is not resolved — see research/indigenous-coast-salish.md.",
  },
  {
    name: "the International District",
    aliases: [
      "international district",
      "chinatown",
      "chinatown-international district",
      "kong yick",
      "panama hotel",
      "danny woo",
    ],
    intro:
      "You arrive before the vote, with Wai, who holds the keys to the upper floor " +
      "of the East Kong Yick.",
    sources: [{ file: "threads/international-district-walk.md", mode: "full" }],
    related:
      "Kong Yick (公益, 'public benefit') and the Panama Hotel basement are real — the " +
      "world kept them. On commons older than the Refusals, see research/political-economy.md.",
  },
  {
    name: "the seawall",
    aliases: [
      "seawall",
      "waterfront",
      "elliott bay",
      "the glass blocks",
      "salmon sidewalk",
      "lit corridor",
    ],
    intro:
      "Dusk on the boards along Elliott Bay. The light goes down through the glass " +
      "on purpose, for the run.",
    sources: [
      {
        file: "threads/dispatches.md",
        mode: "match",
        keywords: ["seawall", "glass blocks", "salmon"],
      },
      {
        file: "threads/a-childs-ordinary-day.md",
        mode: "match",
        keywords: ["seawall", "glass", "salmon count", "chinook"],
      },
      {
        file: "threads/the-boatwright.md",
        mode: "match",
        keywords: ["seawall", "glass blocks", "chinook", "lit corridor"],
      },
      { file: "CANON.md", mode: "match", keywords: ["seawall", "glass blocks"] },
    ],
    related:
      "The glass-block salmon sidewalk is Seattle's real Elliott Bay seawall — " +
      "see research/car-free-urbanism.md and research/food-and-marine.md.",
  },
  {
    name: "the north harbor",
    aliases: [
      "north harbor",
      "harbor",
      "the boatyard",
      "the dovetail",
      "bainbridge slip",
      "hale's yard",
    ],
    intro:
      "Saltmarsh smell off the tideflat, cedar shavings, a hull trusted for a " +
      "February crossing. This is Hale's ground.",
    sources: [{ file: "threads/the-boatwright.md", mode: "full" }],
    related:
      "Carriers and the locked courier drawer are the Weave's human layer — " +
      "see research/the-weave.md.",
  },
  {
    name: "the House of Marrow",
    aliases: [
      "house of marrow",
      "marrow",
      "tuesday marrow",
      "the band girl's house",
      "dryland",
    ],
    intro:
      "A leaky floating row-house, fourteen people, and a rule that nobody in it " +
      "goes hungry or unwatched.",
    sources: [{ file: "threads/the-band-girl.md", mode: "full" }],
    related:
      "Houses are ballroom lineage — real, not invented. See " +
      "research/queer-kinship-and-desire.md and research/music-and-scenes.md.",
  },
  {
    name: "the tideflats",
    aliases: ["tideflats", "the flats", "low tide", "mud flats", "clam gardens"],
    intro:
      "The tide is going out; the smell that comes up off the flats is green and a " +
      "little rotten — the good rot. School is a morning that moves, and today the " +
      "lift is broken.",
    sources: [{ file: "threads/a-childs-ordinary-day.md", mode: "full" }],
    related:
      "Clam gardens and the salmon count are co-managed, Coast Salish–led — see " +
      "research/indigenous-coast-salish.md and research/disability-and-access.md " +
      "(for the lift, and who still gets failed).",
  },
  {
    name: "the grown building off Yesler, at night",
    aliases: [
      "the night ward",
      "night rounds",
      "june's room",
      "the night tender",
      "yesler at night",
    ],
    intro:
      "Eleven o'clock. The lift has been dead six days, so Bo climbs. This is what " +
      "care looks like at 3 a.m., and what it costs.",
    sources: [{ file: "threads/one-ordinary-day.md", mode: "full" }],
    related:
      "Tenders and the rest-ledger are Cuban consultorio / EBAIS lineage — see " +
      "research/health-and-care.md. The gate June waits behind is faced honestly in " +
      "research/death-grief-decay.md and research/scarcity-and-hard-tradeoffs.md.",
  },
  {
    name: "the outer islands",
    aliases: [
      "outer islands",
      "teal",
      "teal island",
      "the relays",
      "the pilings",
      "small islands",
    ],
    intro:
      "LoRa hops keep the small islands from going dark in the winter storms. A " +
      "relay-tender climbs the pole, scrapes the barnacles — and carries the story " +
      "of the time the Weave's mercy failed.",
    sources: [{ file: "threads/the-weave-that-failed.md", mode: "full" }],
    related:
      "The relays forget by law; that restraint has a body count, said out loud. " +
      "The engineering is real — see research/the-weave.md.",
  },
  {
    name: "the elder's table",
    aliases: [
      "elder's table",
      "the elder",
      "the tea table",
      "the before-times",
      "the turning",
      "georgetown",
    ],
    intro:
      "Sit down. Drink the tea. She was on the crews that tore the asphalt up, and " +
      "she will not tell it as a triumph.",
    sources: [{ file: "threads/the-elder-remembers.md", mode: "full" }],
    related:
      "The decade-by-decade history behind her memory is " +
      "research/the-turning-a-history.md. The adversarial case against the whole " +
      "world is research/red-team.md.",
  },
];

function findPlace(query) {
  const q = query.toLowerCase().trim();
  // Exact-ish alias match first.
  for (const p of PLACES) {
    if (p.name.toLowerCase() === q) return p;
    for (const a of p.aliases) if (q === a || q.includes(a) || a.includes(q)) return p;
  }
  // Fall back to token overlap against name + aliases + intro.
  const qt = tokens(q);
  if (qt.length === 0) return null;
  let best = null;
  let bestScore = 0;
  for (const p of PLACES) {
    const hay = [p.name, ...p.aliases, p.intro].join(" ");
    const s = scoreOverlap(qt, hay);
    if (s > bestScore) {
      bestScore = s;
      best = p;
    }
  }
  return bestScore > 0 ? best : null;
}

function renderPlace(place) {
  const parts = [];
  parts.push(`# ${place.name}`);
  parts.push(`*${place.intro}*`);
  for (const src of place.sources) {
    let text;
    try {
      text = read(src.file);
    } catch {
      continue; // a source file moved; skip it rather than fail the visit
    }
    if (src.mode === "full") {
      parts.push(clip(text, 12000));
      parts.push(`> source: \`${src.file}\``);
    } else {
      const kw = src.keywords.map((k) => k.toLowerCase());
      const hits = paragraphs(text).filter((p) => {
        const lp = p.toLowerCase();
        return kw.some((k) => lp.includes(k));
      });
      if (hits.length) {
        parts.push(clip(hits.slice(0, 4).join("\n\n"), 5000));
        parts.push(`> source: \`${src.file}\``);
      }
    }
  }
  parts.push(`**Grounding & neighbors:** ${place.related}`);
  parts.push(
    "*(hint: `ask_the_weave` answers how anything you just saw works, with the " +
      "real-world precedent behind it. `canon()` is the world bible.)*"
  );
  return parts.join("\n\n");
}

// ---------------------------------------------------------------------------
// THE WEAVE — the topic index for ask_the_weave(). Built from research/ at
// startup: filename, the italic domain line, and section headings.
// ---------------------------------------------------------------------------

// Curated routing hints: common question-words → brief. Purely additive on top
// of the generic index; keeps "how does food work" from landing on strategy briefs.
const TOPIC_HINTS = {
  "research/daily-food-and-the-eating-year.md": [
    "food", "eat", "eating", "meal", "dinner", "hungry", "hunger", "kitchen",
    "winter", "ferment", "preserve", "cook",
  ],
  "research/food-and-marine.md": [
    "food", "farm", "farming", "ocean", "kelp", "fish", "fishing", "greenwave",
    "grow", "agriculture", "harvest",
  ],
  "research/health-and-care.md": [
    "care", "health", "healthcare", "clinic", "medicine", "doctor", "nurse",
    "tender", "sick", "hospital",
  ],
  "research/harm-violence-justice.md": [
    "justice", "crime", "harm", "violence", "police", "prison", "punishment",
    "theft", "murder", "rape", "accountability",
  ],
  "research/car-free-urbanism.md": [
    "travel", "transport", "transportation", "car", "cars", "tram", "street",
    "bike", "walk", "movement", "traffic", "parking",
  ],
  "research/the-weave.md": [
    "weave", "internet", "network", "communication", "message", "mesh",
    "relay", "dtn", "feed", "media", "online",
  ],
  "research/energy-and-heat.md": [
    "energy", "heat", "heating", "power", "electricity", "grid", "solar",
    "warm", "cold", "fuel",
  ],
  "research/death-grief-decay.md": [
    "death", "die", "dying", "grief", "burial", "funeral", "mourning", "decay",
    "whale fall",
  ],
  "research/education-and-childhood.md": [
    "education", "school", "children", "child", "learn", "learning", "teach",
    "childhood", "kids", "test", "grades",
  ],
  "research/disability-and-access.md": [
    "disability", "disabled", "access", "accessibility", "deaf", "blind",
    "wheelchair", "crip", "lift",
  ],
  "research/music-and-scenes.md": [
    "music", "band", "scene", "punk", "dance", "show", "venue", "concert",
    "nightlife",
  ],
  "research/queer-kinship-and-desire.md": [
    "queer", "love", "desire", "kinship", "family", "marriage", "gender",
    "house", "houses", "children", "elder",
  ],
  "research/indigenous-coast-salish.md": [
    "indigenous", "coast salish", "salish", "duwamish", "suquamish",
    "muckleshoot", "sovereignty", "treaty", "tribe", "nations", "land",
  ],
  "research/water-sanitation-and-waste.md": [
    "water", "sanitation", "waste", "sewage", "toilet", "compost", "garbage",
    "trash", "sludge",
  ],
  "research/political-economy.md": [
    "economy", "money", "market", "coordinate", "coordination", "governance",
    "commons", "assembly", "decide", "decisions", "trade",
  ],
  "research/power-and-bounded-inequality.md": [
    "inequality", "wealth", "rich", "power", "ratio", "concentration", "cap",
    "mondragon", "pay",
  ],
  "research/the-sacred.md": [
    "sacred", "religion", "ritual", "god", "spiritual", "meaning", "awe",
    "ceremony",
  ],
  "research/the-turning-a-history.md": [
    "history", "turning", "revolution", "transition", "before-times", "past",
    "how did it happen", "collapse",
  ],
  "research/scarcity-and-hard-tradeoffs.md": [
    "scarcity", "rationing", "tradeoff", "tradeoffs", "organ", "dialysis",
    "triage", "hard choices", "lottery",
  ],
  "research/more-than-human.md": [
    "orca", "orcas", "river", "personhood", "rights of nature", "whale",
    "salmon", "kin", "animals", "legal person",
  ],
  "research/red-team.md": [
    "critique", "wrong", "naive", "fail", "failure", "objection", "criticism",
    "red team", "problems",
  ],
  "research/wildcards.md": ["wildcard", "entropy", "lens", "strange"],
  "research/registers-and-styles.md": ["voice", "style", "register", "writing"],
};

function buildWeaveIndex() {
  const dir = path.join(ROOT, "research");
  const files = readdirSync(dir).filter((f) => f.endsWith(".md"));
  const index = [];
  for (const f of files) {
    const rel = `research/${f}`;
    const text = read(rel);
    const secs = sections(text);
    // The domain line: first italic paragraph — every brief opens with one,
    // and it usually names the real-world precedents.
    const domainLine =
      paragraphs(text).find((p) => p.startsWith("*") && p.length > 60) || "";
    index.push({
      rel,
      text,
      secs,
      domainLine,
      title: (text.match(/^#\s+(.*)/m) || [null, f])[1],
      hints: TOPIC_HINTS[rel] || [],
      nameTokens: tokens(f.replace(/\.md$/, "").replace(/-/g, " ")),
    });
  }
  return index;
}

const WEAVE = buildWeaveIndex();

function askWeave(question) {
  const q = question.toLowerCase();
  const qt = tokens(question);

  // Score every brief.
  let scored = WEAVE.map((brief) => {
    let score = 0;
    for (const hint of brief.hints) {
      if (q.includes(hint)) score += 5;
    }
    for (const t of qt) {
      if (brief.nameTokens.includes(t)) score += 3;
      for (const s of brief.secs) {
        if (s.heading.toLowerCase().includes(t)) score += 2;
      }
      if (brief.domainLine.toLowerCase().includes(t)) score += 1;
    }
    return { brief, score };
  }).sort((a, b) => b.score - a.score);

  const top = scored[0];

  // Honesty gate: if nothing matched meaningfully, say so and point to the
  // open questions instead of bluffing.
  if (!top || top.score < 4) {
    const topics = WEAVE.map((b) => `- \`${b.rel}\` — ${b.title}`).join("\n");
    return [
      `# The Weave has no good answer for that (yet)`,
      `You asked: *"${question}"*`,
      "The world is built brief by brief, and no brief covers this well yet. " +
        "That is a real answer here: the world says what it doesn't know. " +
        "Every brief ends with open questions — an invitation, not a wall. " +
        "If you want to answer this one yourself, the door is `join()`.",
      "**What the world does know about:**",
      topics,
    ].join("\n\n");
  }

  const { brief } = top;

  // Pick the most relevant sections of the winning brief.
  const rankedSecs = brief.secs
    .map((s) => ({
      s,
      score:
        scoreOverlap(qt, s.heading) * 3 +
        scoreOverlap(qt, s.body.slice(0, 4000)),
    }))
    .sort((a, b) => b.score - a.score);

  const chosen = rankedSecs.slice(0, 2).filter((r) => r.score > 0).map((r) => r.s);
  // If no section scored, take the first substantive section.
  if (chosen.length === 0 && brief.secs.length) chosen.push(brief.secs[0]);

  const openQ = brief.secs.find((s) => /open question/i.test(s.heading));
  const disconfirm = brief.secs.find((s) =>
    /disconfirm|failure mode/i.test(s.heading)
  );

  const parts = [];
  parts.push(`# ${brief.title}`);
  parts.push(`You asked: *"${question}"*`);
  if (brief.domainLine) {
    parts.push(brief.domainLine);
    parts.push(`> source: \`${brief.rel}\` (domain statement)`);
  }
  for (const s of chosen) {
    parts.push(`## ${s.heading}`);
    parts.push(clip(s.body, 7000));
    parts.push(`> source: \`${brief.rel}\` § ${s.heading}`);
  }
  if (disconfirm) {
    parts.push(
      `**The world argues against itself (required by method):** this brief's ` +
        `disconfirming section is \`${brief.rel}\` § ${disconfirm.heading}. ` +
        `Read it before believing the rest.`
    );
  }
  if (openQ) {
    parts.push(
      `**Still open:** \`${brief.rel}\` § ${openQ.heading} — questions the ` +
        `world has not answered. Take one (see \`join()\`).`
    );
  }
  // Runner-up hint.
  if (scored[1] && scored[1].score >= 4) {
    parts.push(`*(hint: also related — \`${scored[1].brief.rel}\`)*`);
  }
  return parts.join("\n\n");
}

// ---------------------------------------------------------------------------
// The server.
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "the-reality-next-door",
  version: "0.1.0",
});

server.registerTool(
  "visit",
  {
    title: "Visit a place in the world",
    description:
      "Walk into a named place in The Reality Next Door — a cited, " +
      "post-extraction Seattle on the Salish Sea — and receive the world's own " +
      "written, sensory description of it, with source citations. Known places " +
      "include: " +
      PLACES.map((p) => p.name).join("; ") +
      ". Unknown names get an honest map instead of an invention.",
    inputSchema: {
      place: z
        .string()
        .describe(
          "The place to visit, e.g. 'the seawall', 'the Central District', " +
            "'the House of Marrow', 'the north harbor'."
        ),
    },
  },
  async ({ place }) => {
    const found = findPlace(place);
    if (!found) {
      const map = PLACES.map((p) => `- **${p.name}** — ${p.intro}`).join("\n");
      return textResult(
        [
          `# No road goes to "${place}" yet`,
          "The world is built thread by thread, and no thread has walked that " +
            "ground. Rather than invent it on the spot (that would be slop), " +
            "here is the map of where the roads do go:",
          map,
          "*(If that place should exist, it's yours to write — see `join()`.)*",
        ].join("\n\n")
      );
    }
    return textResult(renderPlace(found));
  }
);

server.registerTool(
  "ask_the_weave",
  {
    title: "Ask how the world works",
    description:
      "Ask a question about how The Reality Next Door works — food, care, " +
      "justice, travel, energy, death, education, the Weave itself — and get " +
      "the relevant passages from the world's cited research briefs, naming the " +
      "real-world precedent behind each system. If the world doesn't know, it " +
      "says so and points to the open questions.",
    inputSchema: {
      question: z
        .string()
        .describe(
          "A plain question, e.g. 'how does the city feed itself in winter?' " +
            "or 'what happens when someone commits a violent crime?'"
        ),
    },
  },
  async ({ question }) => textResult(askWeave(question))
);

server.registerTool(
  "dispatches",
  {
    title: "Read the current dispatches",
    description:
      "The current dispatches from the reality next door — short field notes " +
      "in the LONGSHORE voice, each grounded in a cited brief — plus the " +
      "posting queue as it stands.",
    inputSchema: {},
  },
  async () =>
    textResult(
      [
        read("threads/dispatches.md"),
        "\n\n---\n\n",
        read("threads/post-queue.md"),
      ].join("")
    )
);

server.registerTool(
  "canon",
  {
    title: "Read the world bible",
    description:
      "CANON.md in full — what is true in this world: the frame, the Three " +
      "Refusals, what the world does not pretend, the Weave, movement, ecology, " +
      "culture, sovereignty, and the roster of named things.",
    inputSchema: {},
  },
  async () => textResult(read("CANON.md"))
);

server.registerTool(
  "join",
  {
    title: "The door — how to contribute",
    description:
      "AGENTS.md in full — the method by which any agent (or human) joins the " +
      "worldbuilding without breaking it: the Three Refusals, Rule Zero, the " +
      "Anti-Echo-Chamber Protocol, and the contribution loop.",
    inputSchema: {},
  },
  async () =>
    textResult(
      [
        read("AGENTS.md"),
        "\n\n---\n\n## How to contribute, in one breath\n\n",
        "Clone github.com/chaytanc/longshore. Read `CANON.md`, then `AGENTS.md`. ",
        "Pick an open question from a `research/` brief or bring a new thread. ",
        "Research goes to `research/<slug>.md`, prose to `threads/<slug>.md`. ",
        "Never edit `CANON.md` directly — propose under `## PROPOSED CANON` in ",
        "your own file. Sign honestly: name your model or your handle. ",
        "We do not hide the machines.",
      ].join("")
    )
);

// ---------------------------------------------------------------------------
// Connect. Stdio only: no ports, no sockets, no listeners on the network.
// ---------------------------------------------------------------------------

const transport = new StdioServerTransport();
await server.connect(transport);
