#!/usr/bin/env node
/**
 * Smoke test for the mcp-template: spawn the server over stdio as a real MCP
 * client would, list the tools, and exercise visit() and ask_the_world().
 *
 * By default it points the server at the directory two levels up (this
 * template ships inside the parent repo at seed-kit/mcp-template/, so the
 * parent world is the test fixture). Set WORLD_ROOT to test against your own
 * world instead:
 *
 *   WORLD_ROOT=/path/to/your/world npm test
 */

import { fileURLToPath } from "node:url";
import path from "node:path";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WORLD_ROOT = process.env.WORLD_ROOT || path.resolve(HERE, "..", "..");

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
  env: { ...process.env, WORLD_ROOT },
});

await client.connect(transport);

// 1. tools/list — the four doors (dispatches only if configured)
const { tools } = await client.listTools();
const names = tools.map((t) => t.name).sort();
check(
  "tools/list exposes the doors",
  ["ask_the_world", "canon", "join", "visit"].every((n) => names.includes(n)),
  names.join(", ")
);

// 2. visit a configured place
const somewhere = firstText(
  await client.callTool({ name: "visit", arguments: { place: "the seawall" } })
);
check(
  "visit(configured place) returns text with a source citation",
  /source: `/.test(somewhere)
);

// 3. visit an unknown place → honest map, no invention
const nowhere = firstText(
  await client.callTool({
    name: "visit",
    arguments: { place: "the moon colony" },
  })
);
check("visit(unknown) answers honestly with the map", /No road goes to/.test(nowhere));

// 4. ask_the_world — a question the briefs should cover
const answered = firstText(
  await client.callTool({
    name: "ask_the_world",
    arguments: { question: "how does the city feed itself in winter?" },
  })
);
check(
  "ask_the_world(covered) cites a research brief",
  new RegExp("source: `research/").test(answered)
);

// 5. ask_the_world — nonsense → honest ignorance
const unknown = firstText(
  await client.callTool({
    name: "ask_the_world",
    arguments: { question: "zorbulon quantum blockchain lasers" },
  })
);
check(
  "ask_the_world(nonsense) admits ignorance instead of bluffing",
  /no good answer/i.test(unknown)
);

// 6. canon / join
const canon = firstText(await client.callTool({ name: "canon", arguments: {} }));
check("canon() returns the world bible", canon.length > 200);

const join = firstText(await client.callTool({ name: "join", arguments: {} }));
check("join() returns the method file", join.length > 200);

await client.close();
console.log(process.exitCode ? "\nSome checks failed." : "\nAll checks passed.");
