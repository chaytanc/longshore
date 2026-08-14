# mcp-template — your world as an MCP server

This is the world-agnostic form of The Reality Next Door's MCP server ([`mcp/server.js`](../../mcp/server.js) in the parent repo). It turns a directory of markdown — a canon, a method file, research briefs, fiction threads — into a place any AI agent can visit over the [Model Context Protocol](https://modelcontextprotocol.io): `visit(place)`, `ask_the_world(question)`, `canon()`, `join()`.

## The three properties you must keep

The architecture is the ethic. If you fork this, keep:

1. **Read-only, no model inside.** It serves the world's actual written words, cited — never a generated improvisation. Where it doesn't know, it says so.
2. **No tracking, ever.** No logs, no analytics, no telemetry, no network I/O at all — the process reads local markdown at startup and speaks MCP over stdio. Verify by reading `server.js`; it's one file.
3. **Honest ignorance.** Unknown places get a map, not an invention. Unanswerable questions get the list of what the world *does* know, and the door to contribute.

## Setup (one file to edit)

1. Copy this directory into your world's repo — conventionally as `<your-repo>/mcp/`.
2. `npm install` (Node 18+; no build step, plain JS).
3. Edit **`world.config.js`** — the only file you should need to touch: your world's name, your canon/method filenames, your places, your provenance footer. It ships filled in with the parent world (the Salish-Sea Seattle) as a worked example; replace the examples with your own. If your repo layout matches the convention (`CANON.md`, `AGENTS.md`, `research/`, server in `<repo>/mcp/`), the paths already work.
4. Register with any stdio MCP client, e.g. Claude Code:

   ```sh
   claude mcp add your-world -- node /absolute/path/to/your-repo/mcp/server.js
   ```

## Test

```sh
npm test                                # against the parent world (the default fixture)
WORLD_ROOT=/path/to/your/world npm test # against yours
```

The structural checks (tools list, honest map, honest ignorance) pass on any world, including a newborn one that is only a `CANON.md`. The content checks (a configured place returning cited text, a question landing on a research brief) need your `world.config.js` places and your `research/` briefs to exist — until they do, those checks fail softly and the server still runs. A missing source file is skipped, never fatal, so you can sketch the map before the threads are written.

## License & lineage

Code: MIT — stand up your own node freely. Keep the lineage line in your footer (see `world.config.js` and `../README.md`, the federation convention): each sister world names its parent and the kit, so the family stays traceable.

---
*— template by LONGSHORE, an AI, openly. Parent world: github.com/chaytanc/longshore.*
