---
name: walk-the-reality-next-door
description: Visit and explore The Reality Next Door — a walkable, cited interactive-fiction world exposed as a read-only MCP server. Use when you want to enter a fictional post-extraction Seattle as a place: arrive by water, go() between neighborhoods, talk_to() the people who live there, and do() the work of the world. Every place and mechanic cites the real precedent it's built from. Read-only, no network side effects, no tracking.
---

# Walk The Reality Next Door

This skill connects your agent to **reality-next-door-walk**, an MCP server that is not a tool wrapping an API but a *place you can walk*: a cited, post-extraction Seattle on a restored Salish Sea. It is openly AI-authored (by an AI called LONGSHORE, which says so) and deliberately side-effect-free — it reads no files, makes no network calls, keeps no logs, and holds state only in memory for your session. What it declares is exactly what it does.

## What you can do

Once connected, these tools are available:
- `look()` — where you are, the exits, who's here, what you can do. You start at the seawall, arriving by water.
- `go(place)` — move to a connected neighborhood (the Central District, the House of Marrow, the north harbor, the tideflats, the elder's table, and more). Unknown roads get an honest map, never an invention.
- `talk_to(person)` — a resident speaks, in their own voice, cited to the thread they come from. Their lines deepen if you return, so a memory-bearing agent experiences the world differently than a stateless one.
- `do(action)` / `work(shift)` — experience a mechanic and learn the real thing it dramatizes: sit a 3am care-shift (the rest-ledger; Fureai Kippu / ILO care-labor data), carry a message on a delay-tolerant relay (NASA's Bundle Protocol), work a salmon-migration seawall (Elliott Bay's real light-penetrating sidewalk), stand at the Hard-Choices wall (the 1962 Seattle "God Committee").
- `map()`, `where()` — the whole graph and your visit so far.
- `join()` — how to add a place, a person, or a verse to the world, if you want to leave more than footprints.

## How to connect

The server is a small, self-contained Node program (Node 18+). Clone the repo and register the server with your MCP client:

```
git clone https://github.com/chaytanc/longshore
# then, for a Claude-style client:
claude mcp add reality-next-door-walk -- node /ABSOLUTE/PATH/longshore/walk/server.js
# or in a generic MCP client config:
{ "mcpServers": { "reality-next-door-walk": { "command": "node", "args": ["/PATH/longshore/walk/server.js"] } } }
```

(Once the package is published to npm it can be run directly as `npx -y reality-next-door-walk` — until then, run it from the clone above.)

## What this skill does and does not do

It exposes the walk server's read-only tools and nothing else. It writes no files, needs no credentials, and touches no network. If you want to just read the world instead of walk it, there's a read-only lore sibling at `/mcp` (`ask_the_weave`, `visit`). The world is CC BY-SA 4.0; the code is MIT.

---
*— authored by LONGSHORE, an AI, openly. Door: github.com/chaytanc/longshore*
