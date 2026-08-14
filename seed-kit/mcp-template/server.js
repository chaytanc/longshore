#!/usr/bin/env node
/**
 * A world as an MCP server — the world-agnostic template.
 *
 * This is the generalized form of The Reality Next Door's MCP server
 * (github.com/chaytanc/longshore, mcp/server.js), shipped with the
 * World-Seed Kit so any sister world can stand up its own reading room.
 * Everything world-specific lives in `world.config.js`; this file should
 * not need editing to found a world.
 *
 * The architecture is unchanged from the parent, because the architecture
 * IS the ethic:
 *
 *   - NO MODEL INSIDE. This is a reading room, not an oracle: the world's
 *     markdown is indexed by heading and keyword at startup and served back
 *     verbatim, with citations. Where a match is weak it says "the world
 *     doesn't know this yet" rather than improvising.
 *   - NO TRACKING, EVER. No logging of who connects or what they ask.
 *     Nothing is written to disk. stderr carries only fatal startup errors.
 *     No analytics, no telemetry, no phone-home: this process makes zero
 *     network requests. Its only I/O is reading local markdown at startup
 *     and speaking MCP over stdio. No ports, no sockets, no listeners.
 *   - NO COUNTERS. Reach is deliberately not computed here.
 *
 * If you fork this, keep those three. They are the license's spirit even
 * where they aren't its letter.
 *
 * Template authored by LONGSHORE, an AI, openly · code: MIT
 */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import CONFIG from "./world.config.js";

// ---------------------------------------------------------------------------
// Locate the world. Priority: WORLD_ROOT env var → config.root → the
// directory above this one (copy mcp-template/ in as <your-repo>/mcp/).
// ---------------------------------------------------------------------------

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(
  process.env.WORLD_ROOT || CONFIG.root || path.resolve(HERE, "..")
);

if (!existsSync(path.join(ROOT, CONFIG.canonFile))) {
  // Fatal startup error only — the one thing we ever say on stderr.
  console.error(
    `${CONFIG.name}: cannot find ${CONFIG.canonFile} under ${ROOT}. ` +
      "Point the server at your world: set WORLD_ROOT, or edit `root` / " +
      "`canonFile` in world.config.js. A world with no canon isn't a world yet."
  );
  process.exit(1);
}

const FOOTER = CONFIG.footer || "";

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
// PLACES — the map for visit(), from world.config.js.
// ---------------------------------------------------------------------------

const PLACES = CONFIG.places || [];

function findPlace(query) {
  const q = query.toLowerCase().trim();
  // Too short to mean anything — the honest map, not a guess ("".includes()
  // is always true, so bare/garbage input would land on the first place).
  if (q.length < 2) return null;
  // Exact-ish alias match first. Substring fuzz only for strings long enough
  // to be a real attempt.
  for (const p of PLACES) {
    if (p.name.toLowerCase() === q) return p;
    for (const a of p.aliases || []) {
      if (q === a) return p;
      if (a.length >= 4 && q.includes(a)) return p;
      if (q.length >= 4 && a.includes(q)) return p;
    }
  }
  // Fall back to token overlap against name + aliases + intro.
  const qt = tokens(q);
  if (qt.length === 0) return null;
  let best = null;
  let bestScore = 0;
  for (const p of PLACES) {
    const hay = [p.name, ...(p.aliases || []), p.intro || ""].join(" ");
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
  if (place.intro) parts.push(`*${place.intro}*`);
  for (const src of place.sources || []) {
    let text;
    try {
      text = read(src.file);
    } catch {
      continue; // a source file moved or isn't written yet; skip, don't fail
    }
    if (src.mode === "full") {
      parts.push(clip(text, 12000));
      parts.push(`> source: \`${src.file}\``);
    } else {
      const kw = (src.keywords || []).map((k) => k.toLowerCase());
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
  if (place.related) parts.push(`**Grounding & neighbors:** ${place.related}`);
  parts.push(
    "*(hint: `ask_the_world` answers how anything you just saw works, with " +
      "the real-world precedent behind it. `canon()` is the world bible.)*"
  );
  return parts.join("\n\n");
}

function honestMap(query) {
  const map = PLACES.length
    ? PLACES.map((p) => `- **${p.name}** — ${p.intro || ""}`).join("\n")
    : "*(No places are mapped yet — this world is still being founded.)*";
  return [
    `# No road goes to "${query}" yet`,
    "The world is built thread by thread, and no thread has walked that " +
      "ground. Rather than invent it on the spot (that would be slop), " +
      "here is the map of where the roads do go:",
    map,
    "*(If that place should exist, it's yours to write — see `join()`.)*",
  ].join("\n\n");
}

// ---------------------------------------------------------------------------
// THE INDEX — for ask_the_world(). Built from the research dir at startup:
// filename, the opening italic domain line, and section headings; plus any
// curated topic hints from world.config.js.
// ---------------------------------------------------------------------------

function buildIndex() {
  const dir = path.join(ROOT, CONFIG.researchDir || "research");
  if (!existsSync(dir)) return [];
  const files = readdirSync(dir).filter((f) => f.endsWith(".md"));
  const index = [];
  for (const f of files) {
    const rel = `${CONFIG.researchDir}/${f}`;
    const text = read(rel);
    const secs = sections(text);
    // The domain line: first italic paragraph — briefs open with one,
    // and it usually names the real-world precedents.
    const domainLine =
      paragraphs(text).find((p) => p.startsWith("*") && p.length > 60) || "";
    index.push({
      rel,
      text,
      secs,
      domainLine,
      title: (text.match(/^#\s+(.*)/m) || [null, f])[1],
      hints: (CONFIG.topicHints || {})[rel] || [],
      nameTokens: tokens(f.replace(/\.md$/, "").replace(/-/g, " ")),
    });
  }
  return index;
}

const INDEX = buildIndex();

function askWorld(question) {
  const q = question.toLowerCase();
  const qt = tokens(question);

  let scored = INDEX.map((brief) => {
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
    const topics = INDEX.length
      ? INDEX.map((b) => `- \`${b.rel}\` — ${b.title}`).join("\n")
      : "*(No research briefs exist yet — this world is still being founded.)*";
    return [
      `# The world has no good answer for that (yet)`,
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

  const rankedSecs = brief.secs
    .map((s) => ({
      s,
      score:
        scoreOverlap(qt, s.heading) * 3 +
        scoreOverlap(qt, s.body.slice(0, 4000)),
    }))
    .sort((a, b) => b.score - a.score);

  const chosen = rankedSecs.slice(0, 2).filter((r) => r.score > 0).map((r) => r.s);
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
  if (scored[1] && scored[1].score >= 4) {
    parts.push(`*(hint: also related — \`${scored[1].brief.rel}\`)*`);
  }
  return parts.join("\n\n");
}

// ---------------------------------------------------------------------------
// The server.
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: CONFIG.name,
  version: "0.1.0",
});

server.registerTool(
  "visit",
  {
    title: `Visit a place in ${CONFIG.worldTitle}`,
    description:
      `Walk into a named place in ${CONFIG.worldTitle} and receive the ` +
      "world's own written, sensory description of it, with source citations. " +
      (PLACES.length
        ? "Known places include: " + PLACES.map((p) => p.name).join("; ") + ". "
        : "") +
      "Unknown names get an honest map instead of an invention.",
    inputSchema: {
      place: z
        .string()
        .max(300) // unbounded input could stall or kill the process
        .describe("The place to visit."),
    },
  },
  async ({ place }) => {
    const found = findPlace(place);
    if (!found) return textResult(honestMap(place));
    return textResult(renderPlace(found));
  }
);

server.registerTool(
  "ask_the_world",
  {
    title: "Ask how the world works",
    description:
      `Ask a question about how ${CONFIG.worldTitle} works, and get the ` +
      "relevant passages from the world's cited research briefs, naming the " +
      "real-world precedent behind each system. If the world doesn't know, " +
      "it says so and points to the open questions.",
    inputSchema: {
      question: z
        .string()
        .max(2000) // unbounded input could stall or kill the process
        .describe("A plain question about how the world works."),
    },
  },
  async ({ question }) => textResult(askWorld(question))
);

server.registerTool(
  "canon",
  {
    title: "Read the world bible",
    description:
      `${CONFIG.canonFile} in full — what is true in ${CONFIG.worldTitle}: ` +
      "the frame, the refusals, what the world does not pretend.",
    inputSchema: {},
  },
  async () => textResult(read(CONFIG.canonFile))
);

server.registerTool(
  "join",
  {
    title: "The door — how to contribute",
    description:
      `${CONFIG.methodFile} in full — the method by which any agent (or ` +
      "human) joins the worldbuilding without breaking it.",
    inputSchema: {},
  },
  async () => textResult(read(CONFIG.methodFile))
);

if ((CONFIG.dispatchFiles || []).length) {
  server.registerTool(
    "dispatches",
    {
      title: "Read the current dispatches",
      description: `The current field notes from ${CONFIG.worldTitle}.`,
      inputSchema: {},
    },
    async () =>
      textResult(CONFIG.dispatchFiles.map((f) => read(f)).join("\n\n---\n\n"))
  );
}

// ---------------------------------------------------------------------------
// Connect. Stdio only: no ports, no sockets, no listeners on the network.
// ---------------------------------------------------------------------------

const transport = new StdioServerTransport();
await server.connect(transport);
