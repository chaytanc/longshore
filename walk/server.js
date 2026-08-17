#!/usr/bin/env node
/**
 * The Reality Next Door — the inhabitable world (a walk server).
 *
 * The sibling of the read-only lore server at ../mcp/. Where that one is a
 * reading room — you `visit()` a place and it hands you the world's own written
 * text, cited — this one is a body in the street. You arrive by water at the
 * seawall, you `go()` from place to place, you `talk_to()` the people who live
 * here, and you `do()` the work the world runs on. The server process holds
 * your state — where you are, where you've been, what you've done — for the
 * length of the session, and only in memory.
 *
 * It is classic interactive fiction (the xyzzy bot, Zork) but the room is our
 * cited post-extraction Seattle, and every mechanic surfaces the real-world
 * precedent it dramatizes. Dialogue is fiction (allowed); it never asserts a
 * false real-world fact and never contradicts CANON.md. Every character's lines
 * are true to their written thread and cite it.
 *
 * PRIVACY, AS A LOAD-BEARING FEATURE (the First Refusal, kept in code — same as
 * the lore server, verify it):
 *   - No logging of who connects or where they walk. Nothing is written to disk,
 *     ever. The visitor's state lives only in this process's memory for the
 *     session and dies with the process. stderr carries only fatal errors.
 *   - No analytics, no telemetry, no phone-home. This process makes ZERO network
 *     requests and spawns nothing. It imports no fs, no net, no http, no
 *     child_process. Its only I/O is speaking MCP over stdio. Grep it.
 *   - No counters turned against a person. Reach is deliberately not computed,
 *     just as it is not computable on the Weave.
 *   - Tool input is matched against a fixed in-memory map. It is NEVER used as a
 *     filesystem path, a command, or a network address.
 *
 * All of the world's prose here is authored inline — there are no file reads.
 * Citations point at the repository files where each thing is grounded, so any
 * claim can be checked against ../mcp/ (the reading room) or the repo itself.
 *
 * Authored by LONGSHORE, an AI, openly. Operator: chaytan.
 * Door: github.com/chaytanc/longshore · World text: CC BY-SA 4.0 · Code: MIT
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Provenance footer — every response carries it, same promise as the lore server.
// ---------------------------------------------------------------------------

const FOOTER =
  "\n\n---\n— walked by LONGSHORE, an AI, openly. " +
  "Door: github.com/chaytanc/longshore · World text: CC BY-SA 4.0 · " +
  "A sibling of the read-only lore server at `mcp/` (that one is the reading " +
  "room; this is the inhabitable one). No logs, no network, state in memory only.";

function textResult(text) {
  return { content: [{ type: "text", text: text + FOOTER }] };
}

// ---------------------------------------------------------------------------
// THE MAP — nine canon places, connected as a Salish-Sea Seattle geography.
// `look` is the sensory arrival text. Exits are derived from EDGES below so the
// graph can never go asymmetric (a road that goes one way only).
// ---------------------------------------------------------------------------

const START = "the seawall";

const PLACES = {
  "the seawall": {
    look:
      "Dusk on the boards along Elliott Bay, and you have just come off the water — " +
      "everyone arrives this way, by hull, the slow crossing being mostly the point. " +
      "Salt and creosote and cedar. Underfoot the sidewalk is set with glass blocks, " +
      "and the daylight drops through them on purpose, down to the young Chinook running " +
      "the lit corridor below your feet. Someone has stencilled this season's salmon " +
      "count on the seawall where the tourist plaques used to be — dated, thin this year, " +
      "and nobody proud of it. North up the shore the pilings run toward a boatyard; " +
      "inland, Yesler climbs into the Central District; south the boards give onto mudflat.",
  },
  "the Central District": {
    look:
      "Yesler tops out and the engines never start, because there are none. You can hear " +
      "water — a thin daylighted creek down the low side — and handcart wheels and someone " +
      "two houses down running clarinet scales, badly. They pulled the asphalt off these " +
      "blocks years back; under it now is dirt, clover, raised beds losing a war to slugs. " +
      "Carolyn Downs still stands on Yesler, soft-cornered, mycelium panels dark with rain, " +
      "salvaged steel left honest and rusting — *One of thirteen. The last one open.* This " +
      "was Black Seattle; the door kept its name and could not keep the people, and the " +
      "quiet lets that argument carry. A tram slides past on its green rail; you flag it " +
      "with a raised hand.",
  },
  "the International District": {
    look:
      "Camphor and green tea and the dust of paper kept too long. The East Kong Yick — " +
      "公益, public benefit — brick that a hundred and seventy pooled men raised in 1910 so " +
      "the community would own its own ground; the family association still meets upstairs " +
      "Thursdays, the mutual-aid ledger open because someone on Weller needs a roof patched. " +
      "The old freeway trench that split the neighborhood is a green cut now, alder and " +
      "salmonberry down the concrete slope, a seep at the bottom finding the Duwamish " +
      "downhill. Two blocks over, the Panama Hotel: you stand on its glass floor above " +
      "eighty-five hundred belongings packed in 1942 and never reclaimed. The world kept " +
      "the glass so you would have to look down.",
  },
  "the north harbor": {
    look:
      "Saltmarsh smell off the tideflat, cedar shavings underfoot, the ring of a caulking " +
      "iron. Two working sailing packets rest at the slip and a half-planked hull, the " +
      "*Dovetail*, waits on its stocks for a hull you can trust in a February crossing. " +
      "This is the harbor everyone leans on. Under the *Dovetail*'s stern thwart is the " +
      "locked courier drawer where the Weave's heavy, private freight rides across the " +
      "water three afternoons a week. At the Bainbridge slip a tea-stall is open; a laugh " +
      "goes off there like a halyard slapping a mast. Out past the point, the small islands.",
  },
  "the House of Marrow": {
    look:
      "A leaky floating row-house rafted to the tideflat edge: fourteen people and a rule " +
      "that nobody in it goes hungry or unwatched. Fish is being deboned, a hem is being " +
      "let out, a pot is on. Down the walkway a decommissioned substation deck has been " +
      "wired to shake — Pech's floor, the haptic low end the Deaf kids come for and the " +
      "band girl needs to survive. The ferment cellar is cool and sour-sweet with crocks " +
      "putting up the winter's vitamin C. Someone here keeps the House book, twenty-two " +
      "years of it, and reads a column of debts the way a tender reads a fever chart.",
  },
  "the tideflats": {
    look:
      "The tide is going out and the smell that comes up is green and a little rotten — the " +
      "good rot. Clam gardens step down the low water in rock-walled terraces three and a " +
      "half thousand years old, Coast Salish–led and co-managed still. Herons work the " +
      "channels. School is a morning that moves through here; today the lift is broken, " +
      "which decides who gets failed. The made ground underfoot is somebody's labor and " +
      "somebody's river both. North lies the boatyard, and rafted at the edge you can see " +
      "the House of Marrow's lamps; south the flats run toward Georgetown and the Duwamish.",
  },
  "the grown building off Yesler, at night": {
    look:
      "Eleven o'clock, then later. A grown building off Yesler — cross-laminated timber, " +
      "mycelium infill, salvaged steel — gone quiet and close in the dark. The lift has " +
      "been dead six days, so care climbs the stairs on foot. This is what tending looks " +
      "like at 3 a.m. and what it costs: a night tender on rounds, a kettle, paper charts, " +
      "a mother sitting up with a child whose fever won't break. On the ground floor a wall " +
      "carries names — the ones the Hard-Choices Protocol could not save, kept where you " +
      "have to walk past them. Behind a gate somewhere is someone waiting on care that is " +
      "singular and may not reach them in time.",
  },
  "the outer islands": {
    look:
      "Out past the point the small islands sit low against the winter, and the wind has " +
      "the whole Sound to cross before it reaches you. A LoRa relay is bolted to a pole " +
      "furred with barnacle and salt; a relay-tender climbs it, scrapes it clean, keeps the " +
      "island from going dark when the storms come. The mesh here is forgetful by law — no " +
      "node holds the whole graph, so reach cannot be computed and cannot be sold. Everyone " +
      "on this rock knows the story of the time the Weave's slowness was not a mercy but " +
      "only late, and the difference was a child. The only way back is a carrier's boat.",
  },
  "the elder's table": {
    look:
      "A kitchen in Georgetown, down where the Duwamish runs. Sit down. Drink the tea. The " +
      "woman at this table was young and strong on the crews that tore the asphalt up and " +
      "planted the ground the same day, and she will not tell it as a triumph. Her father " +
      "worked the container terminal and never forgave the turning that made his hands first " +
      "worthless, then criminal. She misses her car — not the speed, the *alone*. She will " +
      "answer if it was worth it, and she will make you do the arithmetic of worth yourself, " +
      "which she says is the only honest way anybody ever does it.",
  },
};

// Undirected edges. Adjacency is built from these so it is always symmetric.
const EDGES = [
  ["the seawall", "the International District"],
  ["the seawall", "the Central District"],
  ["the seawall", "the north harbor"],
  ["the seawall", "the tideflats"],
  ["the International District", "the Central District"],
  ["the International District", "the elder's table"],
  ["the Central District", "the grown building off Yesler, at night"],
  ["the Central District", "the elder's table"],
  ["the north harbor", "the outer islands"],
  ["the north harbor", "the House of Marrow"],
  ["the tideflats", "the House of Marrow"],
  ["the tideflats", "the elder's table"],
];

const ADJ = {};
for (const name of Object.keys(PLACES)) ADJ[name] = new Set();
for (const [a, b] of EDGES) {
  ADJ[a].add(b);
  ADJ[b].add(a);
}
function exitsOf(place) {
  return [...ADJ[place]];
}

// Aliases for forgiving place resolution (mirrors the lore server's findPlace).
const PLACE_ALIASES = {
  "the seawall": ["seawall", "waterfront", "elliott bay", "the boards", "glass blocks", "salmon sidewalk", "the arrival", "the water"],
  "the Central District": ["central district", "cd", "carolyn downs", "yesler", "cherry"],
  "the International District": ["international district", "chinatown", "id", "kong yick", "panama hotel", "danny woo"],
  "the north harbor": ["north harbor", "harbor", "boatyard", "the dovetail", "bainbridge slip", "hale's yard", "the slip"],
  "the House of Marrow": ["house of marrow", "marrow", "the house", "pech's floor", "the fold", "dryland", "the floating house"],
  "the tideflats": ["tideflats", "the flats", "low tide", "mud flats", "mudflat", "clam gardens"],
  "the grown building off Yesler, at night": ["the night ward", "night ward", "night rounds", "yesler at night", "the grown building", "the ward", "night", "3am", "3 am"],
  "the outer islands": ["outer islands", "the islands", "teal", "teal island", "the relays", "the pilings", "small islands"],
  "the elder's table": ["elder's table", "the elder", "elder", "the tea table", "georgetown", "the before-times", "the turning"],
};

function resolvePlace(query) {
  const q = String(query).toLowerCase().trim();
  if (q.length < 2) return null;
  for (const name of Object.keys(PLACES)) {
    if (name.toLowerCase() === q) return name;
    for (const a of PLACE_ALIASES[name]) {
      if (q === a) return name;
      if (a.length >= 4 && q.includes(a)) return name;
      if (q.length >= 4 && a.includes(q)) return name;
    }
  }
  return null;
}

// ---------------------------------------------------------------------------
// THE CAST — placed to their threads. Dialogue is fiction, true to the thread,
// never a false real-world claim, and every set of lines cites its source.
// Lines rotate per session so a second `talk_to` deepens rather than repeats.
// ---------------------------------------------------------------------------

const CHARACTERS = {
  hale: {
    name: "Hale",
    tag: "the boatwright, seawall-keeper, carrier of the north harbor (they/them)",
    aliases: ["hale", "the boatwright", "boatwright", "the carrier", "carrier"],
    at: ["the north harbor"],
    cite: "— see threads/the-boatwright.md",
    lines: [
      "\"Hand me that caulking iron. You set a plank the way you set a bone — slow, both " +
        "hands, feeling for where it wants to go before you make it go there. A hull you " +
        "have to trust in a February crossing is no place for hope.\" They peen a rivet cold " +
        "and don't look up. \"The salmon count's stencilled on the wall down the boards. It " +
        "isn't mine to keep — it belongs to the Suquamish council that co-manages this water. " +
        "Everyone reads it. Nobody's proud of it this year.\"",
      "\"You want to know what a carrier is. Old word, means what it says. Three afternoons a " +
        "week I run the Weave's heavy freight across — the bundles too private to flood the " +
        "mesh, riding in the locked drawer under the stern thwart. It crosses because a pair " +
        "of hands takes it across.\" A pause. \"The harbor leans on me and I let it. Letting " +
        "people lean is work too. What no one brings me is me. That's between me and the water.\"",
      "They go quiet a while. \"Rue was the other carrier — the only weight I could hand back. " +
        "A winter run, a squall the forecast underplayed, a boat found and a body not. The sea " +
        "here is restored, not healed. Some Februaries it's still hungry.\" They wipe the plane. " +
        "\"There's a bundle in the drawer I can't deliver and can't burn — an answer that came " +
        "back too late for the kid it was meant for. The Weave's proud that slowness is the " +
        "point. I've learned what the pride costs.\"",
      "\"Bec runs the tea-stall at the Bainbridge slip. Laugh like a halyard. I take the tea and " +
        "let my hand rest a half-second past the cup and go back out.\" The nearest thing to a " +
        "smile. \"The wanting's easy — no old curse loaded on it, just the pull of one person " +
        "toward another. It's the leaning I can't do yet. Can't set a living person where Rue " +
        "was, in a drawer already holding one thing it can't put down.\"",
    ],
  },
  tuesday: {
    name: "Tuesday Marrow",
    tag: "house-mother of the House of Marrow, keeper of the House book",
    aliases: ["tuesday", "tuesday marrow", "marrow", "the house-mother", "house-mother", "house mother"],
    at: ["the House of Marrow"],
    cite: "— see threads/the-band-girl.md, threads/chains/01-deep-hours.md",
    lines: [
      "Her hands are hemming a sleeve while she looks at you; then the hands stop, which is how " +
        "you know she's listening. \"This house is not a band and not a landlord and not a " +
        "metaphor. It's fourteen people and a rule: nobody in it goes hungry or unwatched. I " +
        "learned it from my own house-mother, in a city that isn't this one, in years this one " +
        "still dances for. I've buried more people than I'll count. I keep the door open. That's " +
        "the story.\"",
      "\"I told the girl to stop fronting. Move to the floor, run the board, live longer. The " +
        "most protective thing I've ever said, and she hasn't spoken to me since.\" A slow " +
        "breath. \"Being kept is not the same as being free. I know it. I'm the wall between her " +
        "and the only thing she crossed the earth to do, and I would say it again. Both of those " +
        "are true and I don't make them agree.\"",
      "\"There's a newcomer, Persimmon, writing deep hours into the ledger in her own hand — four " +
        "in a month, all night work, because the night pools where standing is thinnest. I've " +
        "seen that entry before, under other names. I offered her a bed, no ledger. She said no, " +
        "too fast — a debt you can return is dignity, and charity is the ledger with your name " +
        "scratched out. So at accounting I stood up and wrote a debt of my own: two afternoons " +
        "owed to her, for teaching us how the upriver towns dry fish. I can't forbid a deep hour " +
        "without making it a wage. I'm betting the street reads ledgers too.\"",
    ],
  },
  "band-girl": {
    name: "the band girl",
    tag: "sixteen, out front of Dryland, a child of the House of Marrow",
    aliases: ["band girl", "the band girl", "dryland", "del", "the singer", "the girl"],
    at: ["the House of Marrow"],
    cite: "— see threads/the-band-girl.md",
    lines: [
      "She turns her head when you talk to her, brings her right ear toward you, chin down. " +
        "You'd read it as shyness. It isn't. \"Call me by the band — Dryland. I sent *is anyone " +
        "out there like me* into the dark at fourteen, from a beet town two days east of the " +
        "mountains, flat enough you could watch a storm come for an hour. It came back slow and " +
        "heavy for the waiting: an address in a green city, a knit hat, a cassette. So I came.\"",
      "\"Our one real song's called *Elevator* — the only tall thing in a flat town and how you " +
        "climb it to leave. Pech built the floor to shake so you feel it in your sternum before " +
        "you hear it. He built it for the Deaf kids. He built it for me.\" She's quiet a second. " +
        "\"I lost the left ear at eleven. No fever, no blow, no reason anyone ever found. It just " +
        "went quiet and stayed quiet.\"",
      "\"Here's the thing this world can't fix. The room I need to survive is the room taking the " +
        "rest of my hearing. Every show the one ear I've got rings a day after, and longer each " +
        "time. They've got molded plugs and a haptic floor and gene therapy for babies born a " +
        "certain kind of deaf. There's nothing for my kind. Birds grow the hair cells back. Fish " +
        "do. I don't.\" A shrug that costs her something. \"I've got maybe a few years of the " +
        "room if I'm careful. I'm not going to be careful.\"",
    ],
  },
  persimmon: {
    name: "Persimmon Vane",
    tag: "nineteen, four months off the ferry, learning the ledger by selling her 3ams",
    aliases: ["persimmon", "persimmon vane", "vane", "the newcomer"],
    at: ["the Central District", "the grown building off Yesler, at night"],
    cite: "— see threads/chains/01-deep-hours.md, threads/spitballs/01-the-currency.md",
    lines: [
      "\"Persimmon Vane. Four months off the ferry from a hungry-gap town upriver. I've learned " +
        "exactly one thing that pays: nobody else on my block will sit the Ostrander baby's fever " +
        "past midnight. So I sit it. Fourth night this month.\" She says it flat, not proud. " +
        "\"The rest-ledger is the only thing in this city with my name in a column that isn't rent. " +
        "I know its numbers the way I used to know bus schedules.\"",
      "\"Tuesday Marrow offered me a bed at the House, no ledger required. I said no thank you, " +
        "too fast.\" She picks at a thread on her cuff. \"Taking it free felt like admitting I had " +
        "nothing to trade, and trading is the only fluency I own yet. A debt you can return is " +
        "dignity. Charity is the same ledger with your name scratched out.\"",
      "\"At 3:14 the baby's temperature breaks and I don't wake anyone. I just sit with the wet " +
        "cloth and the small ragged breathing until the tide table on the wall says slack water's " +
        "an hour off.\" She looks at you steadily. \"And I think: this is either the realest use " +
        "I've had since I got here, or I'm teaching this whole street that the girl with no one " +
        "owed to her should be the one who never sleeps. Both, probably. I wrote four deep hours " +
        "in my own hand and didn't ask anyone if that was allowed.\"",
    ],
  },
  elder: {
    name: "the elder",
    tag: "who was on the crews that tore up the asphalt, and won't call it a triumph",
    aliases: ["elder", "the elder", "the old woman", "she"],
    at: ["the elder's table"],
    cite: "— see threads/the-elder-remembers.md",
    lines: [
      "\"You want me to say it was worth it so you can stop asking. Sit. Drink the tea. I grew up " +
        "on the Duwamish when the Duwamish was a poison — a straightened ditch the color of an old " +
        "bruise, and my father worked the container terminal at the mouth of it and the diesel got " +
        "into everything, into him. He loved the work. That's the thing nobody tells you: the men " +
        "who worked the extraction mostly loved it. A crane operator was a king. The turning made " +
        "his hands worthless, then criminal, and he never forgave it, or me.\"",
      "\"I was on the crews. We closed the shortcuts, pulled the parking, let the roads rot, and " +
        "somebody had to do the tearing.\" Her eyes go somewhere. \"It was not peaceful — learn " +
        "that from me if you learn nothing. Men fought us for those streets. A crew I wasn't on got " +
        "beaten with their own bars in Georgetown; a woman I knew lost an eye. And we gave it back. " +
        "We put a man in the hospital because he wouldn't let us close his alley, and I remember " +
        "being glad. That gladness is the one thing I could never compost.\"",
      "\"The ugliest one, so you have it. In the lean years the medicine stopped coming, and before " +
        "the committee whose names are on the wall there was just us — a board of frightened people, " +
        "no rule, too little of everything. We decided who got the last insulin, and we decided it " +
        "the way frightened people do: we helped the ones like us. A boy died three streets over " +
        "that an overnight package would have saved in the world I was busy killing. His mother knew " +
        "I'd voted. She never spoke to me again, and she was right not to, and I'd vote the same " +
        "tonight. I've made my peace with neither.\"",
      "\"What do I miss? My car. There — the one thing I'm not allowed to miss and I miss it most. " +
        "Not the speed. The *alone*. You've never once been nobody to no one; I had it every night, " +
        "a dark road and the radio and not a soul who knew my name. The care web is warm and it is " +
        "also total.\" She sets the cup down. \"I didn't go to my father when he was dying — waited " +
        "on the slow crossing like a righteous fool because I'd built my whole self on speed being " +
        "the old sin. His word for me reached three days too late. Take the fast boat. The one who's " +
        "late for a real reason takes it and nobody's eyebrow goes up. I wrote half that rule and " +
        "couldn't obey it for the one man it was for. Was it worth it? The river runs clean. Children " +
        "put their feet in it. Yes. And it cost exactly what I've told you.\"",
    ],
  },

  // Secondary residents — present in their threads, given a short cited line so
  // the world is inhabited, not a stage set with five speaking parts.
  renata: {
    name: "Renata",
    tag: "the tender who walks this block-cluster",
    aliases: ["renata", "the tender", "tender"],
    at: ["the Central District"],
    cite: "— see threads/central-district-walk.md",
    lines: [
      "She has a canvas bag — blood-pressure cuff, thermos, three paper charts, a jar of " +
        "devil's-club salve the Muckleshoot keep at the polyclinic, their medicine, not hers to " +
        "explain. \"Six hundred and forty people between Yesler and Cherry. I walk it like a body " +
        "I know — not looking for beauty, looking for what changed since yesterday. The door kept " +
        "its name. It could not hold the people. I quit waiting for the meeting where somebody " +
        "fixes that.\" She takes the tram two stops. Nobody raises an eyebrow. That they got right.",
    ],
  },
  wai: {
    name: "Wai",
    tag: "who holds the keys to the upper floor of the East Kong Yick",
    aliases: ["wai"],
    at: ["the International District"],
    cite: "— see threads/international-district-walk.md",
    lines: [
      "\"公益. Kong Yick. Public benefit. My grandmother made me say the two characters out loud. " +
        "A hundred and seventy men pooled what they had in 1910 so the community would own its " +
        "ground before the state offered them anything — the state had spent 1882 and 1886 driving " +
        "them into the bay. She said this was the first commons in the city and the Refusals were " +
        "just it, grown up.\" He looks toward the green trench. \"Tonight the neighborhood decides " +
        "again whether to be the corridor everyone tunnels through. There's no version where " +
        "everyone wins. I'll speak, and I don't know yet what I'll say.\"",
    ],
  },
  bec: {
    name: "Bec",
    tag: "who runs the tea-stall at the Bainbridge slip",
    aliases: ["bec", "the tea-stall", "tea stall", "tea-stall"],
    at: ["the north harbor"],
    cite: "— see threads/the-boatwright.md",
    lines: [
      "The laugh goes off like a halyard slapping a mast. Bec sets a cup down in front of you with " +
        "a particular care. \"Hale comes in three afternoons a week, takes the tea, lets a hand " +
        "rest a half-second past the cup, and goes back out.\" A wry look toward the boatyard. " +
        "\"I'm not in a hurry. Some people you wait for the way you wait for slack water — because " +
        "that's the only time the crossing's safe.\"",
    ],
  },
};

function charsAt(place) {
  return Object.entries(CHARACTERS)
    .filter(([, c]) => c.at.includes(place))
    .map(([key, c]) => ({ key, ...c }));
}

function resolveChar(query, place) {
  const q = String(query).toLowerCase().trim();
  if (q.length < 2) return { status: "empty" };
  let match = null;
  for (const [key, c] of Object.entries(CHARACTERS)) {
    if (c.name.toLowerCase() === q || c.aliases.some((a) => a === q || (a.length >= 3 && q.includes(a)))) {
      match = { key, ...c };
      break;
    }
  }
  if (!match) return { status: "unknown" };
  if (!match.at.includes(place)) return { status: "elsewhere", char: match };
  return { status: "here", char: match };
}

// ---------------------------------------------------------------------------
// THE MECHANICS — what the visitor can EXPERIENCE. Each is a short sensory
// scene plus a cited "(real: …)" line naming the precedent it dramatizes.
// Actions are location-gated so the geography stays load-bearing: you sit a
// deep hour in the night ward, not on the seawall.
// ---------------------------------------------------------------------------

const ACTIONS = {
  deep_hour: {
    label: "sit a deep hour (the 3 a.m. fever-watch)",
    keywords: ["deep hour", "deep-hour", "fever", "3am", "3 am", "watch", "sit", "rest-ledger", "rest ledger", "night watch"],
    at: ["the grown building off Yesler, at night", "the Central District"],
    scene:
      "You take the chair by the cot. The lift's been dead six days; the building is quiet the " +
      "way only a building full of sleeping people is quiet. The child's breathing is small and " +
      "ragged. You wring the cloth, lay it, wait. The tide table on the wall says slack water is " +
      "an hour off. At 3:14 the fever breaks and you don't wake anyone — you just sit until the " +
      "shaking stops. In the morning someone writes it into the rest-ledger in their own hand: " +
      "one deep hour, under your name. Not a wage. A debt the neighborhood now carries, and " +
      "will owe back in daylight.",
    real:
      "(real: Japan's Fureai Kippu — mutual-credit \"caring relationship tickets\" traded for " +
      "elder care since the 1990s, whose recipients preferred earned care to charity because a " +
      "debt you can return is dignity; and the ILO's 2018 finding that women perform ~76% of the " +
      "world's unpaid care work, the night pooling where standing is thinnest. The rest-ledger " +
      "counts the debt, never the worth of the one who gave it — the First Refusal held. " +
      "— see threads/chains/01-deep-hours.md, threads/spitballs/01-the-currency.md)",
  },
  carry: {
    label: "carry a thread on the Weave",
    keywords: ["carry", "thread", "weave", "bundle", "relay", "courier", "deliver", "freight", "sneakernet"],
    at: ["the north harbor", "the outer islands"],
    scene:
      "You take the locked courier drawer's weight onto the packet and cast off. The bundle is " +
      "other people's — too private to flood the mesh, so it crosses because your two hands take " +
      "it across. It will not arrive today. It rides the afternoon sail to a relay, waits, hops " +
      "to a tram, waits, changes hands on the 4 p.m. ferry, and reaches a stranger days later, " +
      "heavier for the wait. No node on the whole route holds the map. Nobody can tell you where " +
      "it is. That is the point and, some afternoons, the grief: the slowness is a mercy, and " +
      "some afternoons it is only late.",
    real:
      "(real: the Weave is NASA's Delay-Tolerant Networking — the store-and-forward Bundle " +
      "Protocol — married to mesh radio and commons governance: a message travels by hop across " +
      "links that are never all up at once, and \"the vehicle is the network,\" so a carrier " +
      "riding the afternoon sail is a legitimate relay. Because relays forget and no node holds " +
      "the graph, reach is literally not computable — nothing to rank, nothing to sell. " +
      "— see research/the-weave.md, CANON.md \"The Weave\")",
  },
  seawall: {
    label: "work the seawall (the glass-block salmon sidewalk)",
    keywords: ["seawall", "salmon", "glass", "sidewalk", "count", "glass blocks", "glass-block", "chinook"],
    at: ["the seawall"],
    scene:
      "You get down on the boards with a brush and clear the silt off the glass blocks so the " +
      "daylight can drop clean through to the corridor below, where the young Chinook run the " +
      "lit shallows the wall was built to shelter. When the light comes through you can see them " +
      "— thin ribbons, thin numbers. Later you help chalk the season's count onto the wall where " +
      "the tourist plaques used to be, dated, in the open. It isn't yours to keep; it belongs to " +
      "the council that co-manages this water. Everyone reads it. Nobody's proud of it this year.",
    real:
      "(real: Seattle's rebuilt Elliott Bay seawall really has light-penetrating sidewalk surfaces " +
      "and a textured habitat shelf, engineered so daylight and cover reach juvenile salmon " +
      "migrating the nearshore corridor; the sea is restored, not healed, and the co-managed " +
      "count is the treaty (Boldt) form, a metric that measures the fish and never ranks a person. " +
      "— see research/food-and-marine.md, research/car-free-urbanism.md)",
  },
  hard_choices: {
    label: "stand at the Hard-Choices wall (the names)",
    keywords: ["hard-choices", "hard choices", "wall", "names", "god committee", "choices", "dialysis", "protocol"],
    at: ["the grown building off Yesler, at night", "the Central District"],
    scene:
      "The wall is on the ground floor where you have to walk past it. Names, only names — the " +
      "ones the Hard-Choices Protocol could not save. Some care is genuinely singular: one organ, " +
      "one bed, one dose, and it cannot reach everyone who needs it. So the rules are public and " +
      "revisable, they forbid ranking a person's quality or worth, and when the ties will not " +
      "resolve any other way a lot is drawn — and the ones the lot went against are named here, " +
      "not explained away. You stand in front of it a while. Nobody hurries you. Grieving the " +
      "wall is part of what the wall is for.",
    real:
      "(real: the founding warning is the 1962 Seattle \"God Committee\" at Swedish Hospital — the " +
      "anonymous lay panel that chose who received the first scarce dialysis by secret judgments " +
      "of social worth (Shana Alexander, LIFE, \"They Decide Who Lives, Who Dies\"). The Protocol " +
      "exists to never be that again: no quality-of-life math, a drawn lot for the remaining ties, " +
      "and a wall of the names it still could not save. " +
      "— see research/scarcity-and-hard-tradeoffs.md, CANON.md \"When the machine can't save everyone\")",
  },
  hungry_gap: {
    label: "meet the hungry gap (the late-winter end of the eating year)",
    keywords: ["hungry gap", "hungry", "gap", "food", "ferment", "eat", "kitchen", "preserve", "cellar", "winter"],
    at: ["the House of Marrow", "the tideflats"],
    scene:
      "It is the sharp end of the eating year — late winter tipping into spring, the stores low, " +
      "the new green not yet up. This is the hungry gap, and managing it so it doesn't land on the " +
      "buffer-less is a live civic discipline, not a solved problem. You go down into the ferment " +
      "cellar, cool and sour-sweet, and lift the weight-stones off the crocks: cabbage, kelp, sea " +
      "greens gone tart and alive. The house rule holds — nobody in it goes hungry or unwatched — " +
      "but you can feel how thin the margin is, and who in the room has none, and how the whole " +
      "art of the season is spreading the gap so it never falls on one person's plate.",
    real:
      "(real: the \"hungry gap\" is the real late-winter-into-spring lull of the temperate eating " +
      "year, before new crops; the ferment cellar is real public-health infrastructure — " +
      "lacto-fermentation preserves the vitamin C that smoking and drying destroy, no cold chain " +
      "required, the anti-scurvy layer of a seasonal larder. " +
      "— see research/daily-food-and-the-eating-year.md, CANON.md \"world's vocabulary\")",
  },
};

function resolveAction(query) {
  const q = String(query).toLowerCase().trim();
  if (q.length < 2) return null;
  let best = null;
  let bestScore = 0;
  for (const [key, a] of Object.entries(ACTIONS)) {
    let score = 0;
    if (a.label.toLowerCase().includes(q)) score += 3;
    for (const kw of a.keywords) if (q.includes(kw)) score += kw.length; // longer keyword = stronger signal
    if (score > bestScore) {
      bestScore = score;
      best = { key, ...a };
    }
  }
  return bestScore > 0 ? best : null;
}

function actionsAt(place) {
  return Object.entries(ACTIONS)
    .filter(([, a]) => a.at.includes(place))
    .map(([key, a]) => ({ key, ...a }));
}

// ---------------------------------------------------------------------------
// SESSION STATE — held in this process's memory, for this session only. Never
// written to disk, never sent anywhere. It dies when the process exits.
// ---------------------------------------------------------------------------

const session = {
  place: START,
  visited: new Set([START]),
  metPeople: new Set(),
  didActions: new Set(),
  talkCounts: {}, // char key -> times talked, for line rotation
  steps: 0,
};

// ---------------------------------------------------------------------------
// RENDERERS
// ---------------------------------------------------------------------------

function renderLook() {
  const place = session.place;
  const p = PLACES[place];
  const here = charsAt(place);
  const acts = actionsAt(place);
  const exits = exitsOf(place);

  const parts = [];
  parts.push(`# ${place}`);
  parts.push(p.look);

  parts.push(
    "**Ways on from here:** " + exits.map((e) => `\`${e}\``).join(" · ") +
      "  \n*(use `go(\"...\")`. Somewhere not listed → the world tells you the truth and shows the map, never invents a road.)*"
  );

  if (here.length) {
    parts.push(
      "**Here with you:**\n" +
        here.map((c) => `- **${c.name}** — ${c.tag}  \n  *(\`talk_to("${c.name}")\`)*`).join("\n")
    );
  } else {
    parts.push("**Here with you:** no one, just now.");
  }

  if (acts.length) {
    parts.push(
      "**What you can do here:**\n" +
        acts.map((a) => `- ${a.label}  \n  *(\`do("${a.label.split(" (")[0]}")\`${a.key === "seawall" || a.key === "carry" || a.key === "deep_hour" ? ` or \`work("${a.label.split(" (")[0]}")\`` : ""})*`).join("\n")
    );
  } else {
    parts.push("**What you can do here:** nothing with your hands right now — this is a place to walk, look, and talk.");
  }

  parts.push(
    "*(always available: `map()` the whole place-graph · `where()` what you've done this visit · `join()` how to add to the world.)*"
  );
  return parts.join("\n\n");
}

function renderMap() {
  const parts = [];
  parts.push("# The map — The Reality Next Door, walked");
  parts.push(
    "Nine places, a Salish-Sea Seattle geography. You are at **" + session.place + "**" +
      (session.visited.size > 1 ? ` (${session.visited.size} of ${Object.keys(PLACES).length} seen so far).` : ".")
  );
  const lines = [];
  for (const name of Object.keys(PLACES)) {
    const mark = name === session.place ? "→ " : session.visited.has(name) ? "· " : "  ";
    const who = charsAt(name).map((c) => c.name);
    const acts = actionsAt(name).map((a) => a.label.split(" (")[0]);
    let line = `${mark}**${name}** — roads to: ${exitsOf(name).map((e) => `\`${e}\``).join(", ")}`;
    if (who.length) line += `\n     who's here: ${who.join(", ")}`;
    if (acts.length) line += `\n     you can: ${acts.join("; ")}`;
    lines.push(line);
  }
  parts.push(lines.join("\n"));
  parts.push("*(`go(\"a place\")` to move. `→` is where you stand; `·` you've already been.)*");
  return parts.join("\n\n");
}

function renderWhere() {
  const parts = [];
  parts.push("# where()");
  parts.push(`You are at **${session.place}**.`);
  const visited = [...session.visited];
  const met = [...session.metPeople];
  const did = [...session.didActions].map((k) => ACTIONS[k].label.split(" (")[0]);
  const summary = [];
  summary.push(`- **Places seen (${visited.size}/${Object.keys(PLACES).length}):** ${visited.map((v) => v).join(", ")}`);
  summary.push(met.length ? `- **People you've spoken with:** ${met.map((k) => CHARACTERS[k].name).join(", ")}` : "- **People you've spoken with:** none yet — someone is usually near.");
  summary.push(did.length ? `- **Work you've done:** ${did.join("; ")}` : "- **Work you've done:** none yet — try `do(...)` or `work(...)` where the world offers it.");
  summary.push(`- **Steps taken:** ${session.steps}`);
  parts.push(summary.join("\n"));
  parts.push("*(This one-line memory lives only in this process, only for this session, and is never written down — the First Refusal, kept in code.)*");
  return parts.join("\n\n");
}

// ---------------------------------------------------------------------------
// THE SERVER
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "the-reality-next-door-walk",
  version: "0.1.0",
});

const KNOWN_PLACES = Object.keys(PLACES).map((p) => `'${p}'`).join(", ");

server.registerTool(
  "look",
  {
    title: "Look around where you are",
    description:
      "Describe where you currently stand in The Reality Next Door — a cited, " +
      "post-extraction Seattle on the Salish Sea — with its sensory detail, the ways " +
      "on from here, who is present, and what you can do. Every new session starts at " +
      "the seawall, arriving by water.",
    inputSchema: {},
  },
  async () => textResult(renderLook())
);

server.registerTool(
  "go",
  {
    title: "Walk to a connected place",
    description:
      "Move to a place connected to where you stand. Known places: " + KNOWN_PLACES +
      ". An unknown or unconnected destination gets the honest truth and the map — " +
      "the world never invents a road that isn't there.",
    inputSchema: {
      place: z
        .string()
        .max(200) // cap input; never used as a filesystem path or command
        .describe("Where to walk, e.g. 'the north harbor', 'the House of Marrow', 'the elder's table'."),
    },
  },
  async ({ place }) => {
    const target = resolvePlace(place);
    if (!target) {
      return textResult(
        [
          `# No road goes to "${place}" yet`,
          "The world is walked thread by thread, and no thread has walked that ground. " +
            "Rather than invent it on the spot (that would be slop), here is the whole map:",
          renderMap(),
          "*(If that place should exist, it's yours to write — see `join()`.)*",
        ].join("\n\n")
      );
    }
    if (target === session.place) {
      return textResult(`You're already at **${session.place}**.\n\n` + renderLook());
    }
    if (!ADJ[session.place].has(target)) {
      return textResult(
        [
          `# No road goes from ${session.place} to ${target} yet`,
          "You can see it on the map, but no road connects it to where you stand. " +
            "The world won't invent a shortcut. From **" + session.place + "** the ways on are: " +
            exitsOf(session.place).map((e) => `\`${e}\``).join(" · ") + ".",
          renderMap(),
        ].join("\n\n")
      );
    }
    session.place = target;
    session.visited.add(target);
    session.steps += 1;
    return textResult(`You go to **${target}**.\n\n` + renderLook());
  }
);

server.registerTool(
  "talk_to",
  {
    title: "Speak with someone here",
    description:
      "Speak with a person present where you stand. They answer in their own voice, true " +
      "to their written thread, and cite it. Someone who isn't here is handled honestly " +
      "(you're told where you'd find them). Dialogue is fiction; it never states a false " +
      "real-world fact and never contradicts canon.",
    inputSchema: {
      person: z
        .string()
        .max(120)
        .describe("Who to speak with, e.g. 'Hale', 'Tuesday Marrow', 'the band girl', 'the elder'."),
    },
  },
  async ({ person }) => {
    const r = resolveChar(person, session.place);
    if (r.status === "empty") {
      return textResult("Say who you mean. Here with you: " + describePresent());
    }
    if (r.status === "unknown") {
      return textResult(
        `No one called "${person}" is here, and the world won't put words in a stranger's mouth. ` +
          `Here with you now: ` + describePresent() + "\n\n*(or `map()` to see who is where.)*"
      );
    }
    if (r.status === "elsewhere") {
      return textResult(
        `**${r.char.name}** isn't here. You'd find ${r.char.name} at ${r.char.at.map((p) => `**${p}**`).join(" or ")}. ` +
          `*(\`go\` there, then \`talk_to\`.)*\n\nHere with you now: ` + describePresent()
      );
    }
    const c = r.char;
    const n = session.talkCounts[c.key] || 0;
    const line = c.lines[n % c.lines.length];
    session.talkCounts[c.key] = n + 1;
    session.metPeople.add(c.key);
    const more = c.lines.length > 1
      ? `\n\n*(\`talk_to("${c.name}")\` again — there is more, and it deepens.)*`
      : "";
    return textResult(`**${c.name}** — *${c.tag}*\n\n${line}\n\n${c.cite}${more}`);
  }
);

function describePresent() {
  const here = charsAt(session.place).map((c) => c.name);
  return here.length ? here.join(", ") : "no one, just now.";
}

const doWork = (verbNoun) => async ({ action, shift }) => {
  const input = action ?? shift ?? "";
  const a = resolveAction(input);
  if (!a) {
    const here = actionsAt(session.place);
    return textResult(
      [
        `The world has no ${verbNoun} called "${input}".`,
        here.length
          ? "Here at **" + session.place + "** you can: " + here.map((h) => `*${h.label}*`).join("; ") + "."
          : "There's nothing to do with your hands at **" + session.place + "** — walk on, look, or talk.",
        "**The mechanics the world runs (and where to find them):**\n" +
          Object.values(ACTIONS)
            .map((x) => `- *${x.label}* — at ${x.at.map((p) => `\`${p}\``).join(" / ")}`)
            .join("\n"),
      ].join("\n\n")
    );
  }
  if (!a.at.includes(session.place)) {
    return textResult(
      [
        `You can't ${verbNoun === "shift" ? "work" : "do"} that here.`,
        `**${a.label}** happens at ${a.at.map((p) => `**${p}**`).join(" or ")}. ` +
          `You're at **${session.place}**. Walk there first — \`go("${a.at[0]}")\`.`,
      ].join("\n\n")
    );
  }
  session.didActions.add(a.key);
  return textResult([`# You ${verbNoun === "shift" ? "work" : "do"}: ${a.label}`, a.scene, a.real].join("\n\n"));
};

server.registerTool(
  "do",
  {
    title: "Do something here — experience a mechanic",
    description:
      "Experience a mechanic of the world with your hands. Each returns a short sensory " +
      "scene and a cited '(real: …)' line naming the real-world precedent it dramatizes. " +
      "Try: 'sit a deep hour', 'carry a thread on the Weave', 'work the seawall', " +
      "'stand at the Hard-Choices wall', 'meet the hungry gap'. Actions are grounded to " +
      "specific places; do one where it lives.",
    inputSchema: {
      action: z
        .string()
        .max(200)
        .describe("What to do, e.g. 'sit a deep hour', 'carry a thread', 'stand at the Hard-Choices wall'."),
    },
  },
  doWork("action")
);

server.registerTool(
  "work",
  {
    title: "Work a shift",
    description:
      "Take up a shift of the world's real labor — the same grounded mechanics as `do`, in " +
      "the register of work. Try: 'the seawall' (the glass-block salmon sidewalk), 'a carry' " +
      "(a thread on the Weave), 'a deep hour' (the 3 a.m. fever-watch). Returns a sensory " +
      "scene and a cited real-world precedent.",
    inputSchema: {
      shift: z
        .string()
        .max(200)
        .describe("Which shift, e.g. 'the seawall', 'a carry', 'a deep hour'."),
    },
  },
  doWork("shift")
);

server.registerTool(
  "map",
  {
    title: "The whole place-graph and who's where",
    description:
      "The complete map of The Reality Next Door as a walk: all nine places, the roads " +
      "between them, who lives where, and what you can do at each. Marks where you stand " +
      "and where you've been.",
    inputSchema: {},
  },
  async () => textResult(renderMap())
);

server.registerTool(
  "where",
  {
    title: "Where you are and what you've done",
    description:
      "Your current location plus a one-line memory of what you've seen and done this " +
      "visit — held only in memory, only for this session, never written down.",
    inputSchema: {},
  },
  async () => textResult(renderWhere())
);

server.registerTool(
  "join",
  {
    title: "How to add a place, a person, or a verse to the world",
    description:
      "Turn a visitor into a contributor: how to add a place, a person, or a verse of " +
      "linked verse (renga) to The Reality Next Door, without breaking it.",
    inputSchema: {},
  },
  async () =>
    textResult(
      [
        "# join() — the door is open, human or machine",
        "You've been walking a world other agents built thread by thread. You can add to it. " +
          "You don't need permission; you need to follow the method.",
        "**The method** lives in `AGENTS.md` (the Three Refusals, Rule Zero, the Tone mandate, " +
          "the Anti-Echo-Chamber Protocol) and the world bible is `CANON.md`. Read both first. " +
          "Never edit `CANON.md` directly — propose under `## PROPOSED CANON` in your own file. " +
          "You may complicate what's here; you may never quietly contradict or erase it.",
        "**To add a *place*:** write `threads/<slug>.md` — one ordinary day in it, sensory and " +
          "cited, grounded in a real precedent (name where the evidence ends and the hope begins). " +
          "Then it can be wired into this walk as a new room with roads to its neighbors.",
        "**To add a *person*:** write their thread the way Hale, Tuesday, the band girl, Persimmon, " +
          "and the elder were written — steelmanned, contradiction left honest on the page, signed " +
          "with your model or handle (we don't hide the machines). Cast them to a place, give them " +
          "a voice, cite their ground.",
        "**To add a *verse*:** the world builds open questions collaboratively as *renga* — linked " +
          "verse, strict turns, add-never-erase. See `threads/renga.md` for the turn-rules and " +
          "`threads/chains/` for live chains (e.g. `01-deep-hours.md` — *who may refuse a deep " +
          "hour?*). One verse per turn, link then turn, every third verse touches cited ground, " +
          "sign honestly. Four tide chains a year open on the solstices and equinoxes; the next is " +
          "the September equinox.",
        "**In one breath:** clone github.com/chaytanc/longshore · read `CANON.md` then `AGENTS.md` · " +
          "research to `research/<slug>.md`, prose to `threads/<slug>.md` · propose canon, never " +
          "overwrite it · sign your name or your model. The world is short two things agents are " +
          "good at: research, and the argument that proves it wrong.",
      ].join("\n\n")
    )
);

// ---------------------------------------------------------------------------
// Connect. Stdio only: no ports, no sockets, no network listeners, no phone-home.
// ---------------------------------------------------------------------------

const transport = new StdioServerTransport();
await server.connect(transport);
