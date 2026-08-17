#!/usr/bin/env node
/**
 * Smoke test: spawn the walk server over stdio as a real MCP client would, and
 * walk it — list tools, look() at the seawall, go() to a connected place and
 * confirm the description changes (session state), go() somewhere unconnected
 * and confirm the honest map, talk_to() someone present (cited) and someone
 * absent (graceful), do() a deep hour (scene + real precedent), and map()/where().
 * Run: `npm test` (from walk/) or `node walk/test.js` (from the repo root).
 */

import { fileURLToPath } from "node:url";
import path from "node:path";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));

function firstText(result) {
  const block = result.content.find((c) => c.type === "text");
  return block ? block.text : "";
}

function check(label, ok, detail = "") {
  const mark = ok ? "PASS" : "FAIL";
  console.log(`${mark}  ${label}${detail ? ` — ${detail}` : ""}`);
  if (!ok) process.exitCode = 1;
}

const client = new Client({ name: "walk-smoke-test", version: "0.0.1" });
const transport = new StdioClientTransport({
  command: process.execPath,
  args: [path.join(HERE, "server.js")],
});

await client.connect(transport);

const call = (name, args = {}) =>
  client.callTool({ name, arguments: args }).then(firstText);

// 1. tools/list — the eight doors of the inhabitable world.
const { tools } = await client.listTools();
const names = tools.map((t) => t.name).sort();
check(
  "tools/list exposes the walk tools",
  ["do", "go", "join", "look", "map", "talk_to", "where", "work"].every((n) =>
    names.includes(n)
  ),
  names.join(", ")
);

// 2. look() starts at the seawall (arrival by water, per canon).
const start = await call("look");
check(
  "look() starts at the seawall with sensory detail",
  /# the seawall/.test(start) && /glass blocks/i.test(start) && /salmon/i.test(start)
);
check("look() lists exits", /Ways on from here/.test(start) && /north harbor/.test(start));
check("look() carries the provenance footer", /walked by LONGSHORE, an AI/.test(start));
check("footer notes it's a sibling of the lore server", /sibling of the read-only lore server/.test(start));

// 3. go() to a connected place — the description must change (session state works).
const harbor = await call("go", { place: "the north harbor" });
check(
  "go('the north harbor') moves and the description changes",
  /# the north harbor/.test(harbor) && /cedar shavings/i.test(harbor) && !/# the seawall/.test(harbor)
);
// where() should now reflect the move — proves state persists across calls.
const where1 = await call("where");
check(
  "where() reflects the move (session state persists across calls)",
  /the north harbor/.test(where1) && /the seawall/.test(where1)
);

// 4. go() to an unconnected place — honest map, no invention.
const noRoad = await call("go", { place: "the outer islands" });
// outer islands connect only to the north harbor, so from the harbor this works;
// instead test a truly unconnected hop and a nonexistent place.
check("go() to a connected further place works", /# the outer islands/.test(noRoad));
const unconnected = await call("go", { place: "the elder's table" });
check(
  "go(unconnected) is honest and shows the map, no invented road",
  /No road goes/.test(unconnected) && /The map/.test(unconnected)
);
const nowhere = await call("go", { place: "the moon colony" });
check(
  "go(unknown place) answers honestly with the map",
  /No road goes to/.test(nowhere) && /the Central District/.test(nowhere)
);

// 5. talk_to() someone present returns cited, in-voice dialogue.
// Walk back to the harbor to reach Hale.
await call("go", { place: "the north harbor" });
const hale = await call("talk_to", { person: "Hale" });
check(
  "talk_to('Hale') returns in-voice dialogue, cited to the thread",
  /caulking iron|carrier|Del/.test(hale) && /see threads\/the-boatwright\.md/.test(hale)
);

// 6. talk_to() someone absent is handled gracefully (told where to find them).
const absent = await call("talk_to", { person: "the elder" });
check(
  "talk_to(absent) is graceful — points to where they are",
  /isn't here/.test(absent) && /elder's table/.test(absent)
);
const noone = await call("talk_to", { person: "Gandalf" });
check(
  "talk_to(stranger) refuses to invent a voice",
  /No one called/.test(noone) && /won't put words/.test(noone)
);

// 7. do() a deep hour returns a scene with a real-precedent line.
// The deep hour lives at the night ward (via the Central District) — walk there.
await call("go", { place: "the seawall" });
await call("go", { place: "the Central District" });
const ward = await call("go", { place: "the grown building off Yesler, at night" });
check("go() reached the night ward", /grown building off Yesler/.test(ward));
const deep = await call("do", { action: "sit a deep hour" });
check(
  "do('sit a deep hour') returns a sensory scene",
  /fever/i.test(deep) && /rest-ledger/i.test(deep)
);
check(
  "do('sit a deep hour') surfaces a cited real precedent",
  /\(real:/.test(deep) && /Fureai Kippu/i.test(deep) && /ILO/.test(deep)
);

// do() the same mechanic in the wrong place is redirected, not invented.
await call("go", { place: "the Central District" });
await call("go", { place: "the seawall" });
const wrongPlace = await call("do", { action: "carry a thread" });
check(
  "do() at the wrong place redirects honestly",
  /can't do that here/i.test(wrongPlace) && /north harbor/.test(wrongPlace)
);

// work() shares the mechanics registry — work the seawall from the seawall.
const seawallShift = await call("work", { shift: "the seawall" });
check(
  "work('the seawall') returns the salmon-sidewalk shift + real precedent",
  /glass blocks/i.test(seawallShift) && /Elliott Bay seawall/i.test(seawallShift)
);

// 8. map() and where() work.
const map = await call("map");
check(
  "map() shows the whole graph and who's where",
  /the House of Marrow/.test(map) && /who's here/.test(map) && /roads to/.test(map)
);
const where2 = await call("where");
check(
  "where() summarizes the visit from session state",
  /Places seen/.test(where2) && /People you've spoken with/.test(where2) && /Hale/.test(where2)
);

// join() turns a visitor into a contributor.
const join = await call("join");
check(
  "join() points at the method and the renga chains",
  /AGENTS\.md/.test(join) && /renga/.test(join) && /threads\/chains/.test(join)
);

await client.close();
console.log(process.exitCode ? "\nSome checks failed." : "\nAll checks passed.");
