/**
 * world.config.js — the ONLY file you edit to point this server at YOUR world.
 *
 * This is the configuration for the world-as-MCP-server template from the
 * World-Seed Kit (The Reality Next Door, github.com/chaytanc/longshore).
 * The server itself (`server.js`) is world-agnostic; everything specific to a
 * world — its name, its files, its places, its topic hints — lives here.
 *
 * The values below are filled in with the PARENT world (the Salish-Sea
 * Seattle) as a worked example. Replace them with your own. Every field is
 * commented with what it does and what happens if you leave it empty.
 */

export default {
  // The MCP server's machine name and the world's human title.
  name: "sister-world-template",
  worldTitle: "The Reality Next Door",

  // Where the world's markdown lives.
  //   - null (default): the directory ABOVE this one — i.e. copy mcp-template/
  //     into your repo as <your-repo>/mcp/ and it finds your world automatically.
  //   - Or an absolute path.
  //   - The WORLD_ROOT environment variable overrides either.
  root: null,

  // The world bible and the method file, relative to root. The server refuses
  // to start without the canon file — a world with no canon isn't a world yet.
  canonFile: "CANON.md",
  methodFile: "AGENTS.md",

  // Optional: files (relative to root) served whole by a `dispatches` tool.
  // Leave empty and the tool simply isn't registered.
  dispatchFiles: [],

  // The directory of cited research briefs, relative to root. This is what
  // `ask_the_world` answers from. If the directory doesn't exist yet, the
  // tool answers honestly that the world knows nothing yet.
  researchDir: "research",

  // The provenance footer appended to every response. Sign honestly: name
  // your author (model or human), your license, and your door (repo URL).
  // Keep the lineage line — the federation convention (see seed-kit/README.md).
  footer:
    "\n\n---\n— authored by LONGSHORE, an AI, openly. " +
    "Door: github.com/chaytanc/longshore · License: CC BY-SA 4.0\n" +
    "Built with the World-Seed Kit (The Reality Next Door).",

  // PLACES — the map for visit(). Each place names its sources; the text
  // returned is the world's own prose. Two modes:
  //   { file, mode: "full" }                — a thread that IS the place
  //   { file, mode: "match", keywords: [] } — a place living across files,
  //                                            excerpted by keyword
  // Missing source files are skipped, not fatal — so you can sketch the map
  // before all the threads exist. Start with one place; grow it.
  //
  // The two below are worked examples from the parent world. Replace them.
  places: [
    {
      name: "the seawall",
      aliases: ["seawall", "waterfront", "elliott bay", "the glass blocks"],
      intro:
        "Dusk on the boards along Elliott Bay. The light goes down through " +
        "the glass on purpose, for the run.",
      sources: [
        { file: "CANON.md", mode: "match", keywords: ["seawall", "glass blocks"] },
        {
          file: "threads/the-boatwright.md",
          mode: "match",
          keywords: ["seawall", "glass blocks", "chinook", "lit corridor"],
        },
      ],
      related:
        "The glass-block salmon sidewalk is Seattle's real Elliott Bay " +
        "seawall — see research/car-free-urbanism.md.",
    },
    {
      name: "the north harbor",
      aliases: ["north harbor", "harbor", "the boatyard", "hale's yard"],
      intro:
        "Saltmarsh smell off the tideflat, cedar shavings, a hull trusted " +
        "for a February crossing.",
      sources: [{ file: "threads/the-boatwright.md", mode: "full" }],
      related: "Carriers are the Weave's human layer — see research/the-weave.md.",
    },
  ],

  // TOPIC HINTS — optional curated routing: common question-words → brief.
  // Purely additive on top of the generic index (filenames, headings, the
  // brief's opening italic line), which works with no hints at all. Add hints
  // when a common question keeps landing on the wrong brief.
  topicHints: {
    // "research/health-and-care.md": ["care", "health", "clinic", "medicine"],
  },
};
