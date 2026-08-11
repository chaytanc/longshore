#!/usr/bin/env node
/**
 * Smoke test: spawn the server over stdio as a real MCP client would,
 * list the tools, and exercise visit() and ask_the_weave().
 * Run: `npm test` (from mcp/) or `node mcp/test.js` (from the repo root).
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

const client = new Client({ name: "smoke-test", version: "0.0.1" });
const transport = new StdioClientTransport({
  command: process.execPath,
  args: [path.join(HERE, "server.js")],
});

await client.connect(transport);

// 1. tools/list
const { tools } = await client.listTools();
const names = tools.map((t) => t.name).sort();
check(
  "tools/list exposes the five doors",
  ["ask_the_weave", "canon", "dispatches", "join", "visit"].every((n) =>
    names.includes(n)
  ),
  names.join(", ")
);

// 2. visit a named place
const seawall = firstText(
  await client.callTool({ name: "visit", arguments: { place: "the seawall" } })
);
check(
  "visit('the seawall') returns sensory text",
  /glass blocks/i.test(seawall) && /salmon/i.test(seawall)
);
check("visit() cites its sources", /source: `threads\//.test(seawall));
check("visit() carries the provenance footer", /LONGSHORE, an AI/.test(seawall));

// 3. visit by alias
const marrow = firstText(
  await client.callTool({ name: "visit", arguments: { place: "House of Marrow" } })
);
check(
  "visit('House of Marrow') resolves the alias",
  /Tuesday Marrow/.test(marrow) && /the-band-girl\.md/.test(marrow)
);

// 4. visit an unknown place → honest map, no invention
const nowhere = firstText(
  await client.callTool({ name: "visit", arguments: { place: "the moon colony" } })
);
check(
  "visit(unknown) answers honestly with the map",
  /No road goes to/.test(nowhere) && /the Central District/.test(nowhere)
);

// 5. ask_the_weave — a question the briefs cover
const food = firstText(
  await client.callTool({
    name: "ask_the_weave",
    arguments: { question: "how does the city feed itself in winter?" },
  })
);
check(
  "ask_the_weave(food) lands on a food brief and cites it",
  /source: `research\/(daily-food-and-the-eating-year|food-and-marine)\.md`/.test(food)
);
check("ask_the_weave() carries the provenance footer", /CC BY-SA 4\.0/.test(food));

// 6. ask_the_weave — justice
const justice = firstText(
  await client.callTool({
    name: "ask_the_weave",
    arguments: { question: "what happens when someone commits a violent crime?" },
  })
);
check(
  "ask_the_weave(justice) cites harm-violence-justice",
  /harm-violence-justice\.md/.test(justice)
);

// 7. ask_the_weave — something the world doesn't know
const unknown = firstText(
  await client.callTool({
    name: "ask_the_weave",
    arguments: { question: "zorbulon quantum blockchain lasers" },
  })
);
check(
  "ask_the_weave(nonsense) admits ignorance instead of bluffing",
  /no good answer/i.test(unknown)
);

// 8. dispatches / canon / join
const disp = firstText(await client.callTool({ name: "dispatches", arguments: {} }));
check("dispatches() returns the dispatches", /DISPATCH 01/.test(disp));

const canon = firstText(await client.callTool({ name: "canon", arguments: {} }));
check("canon() returns CANON.md", /The Three Refusals/.test(canon));

const join = firstText(await client.callTool({ name: "join", arguments: {} }));
check(
  "join() returns AGENTS.md + the contribution note",
  /Anti-Echo-Chamber Protocol/.test(join) && /How to contribute, in one breath/.test(join)
);

await client.close();
console.log(process.exitCode ? "\nSome checks failed." : "\nAll checks passed.");
