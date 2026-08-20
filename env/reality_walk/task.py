"""The "walk and learn" task: grounded field questions, canon grading, and the
episode engine shared by both the OpenEnv and the Verifiers adapters.

The task is deliberately NOT trivia over a text dump. Each field question can
only be answered by *walking* the world served over MCP — going to the right
place, talking to the right person, or doing the right work. The verifier checks
submitted answers against expected canon keywords and, crucially, tells the
agent what it got right, what it missed, and which repository file grounds the
truth. A small, honest exploration term rewards reaching the relevant place or
doing the relevant action, so the questions can't be answered from the lobby.

Honesty note (kept in the open): the folk currency name "tides" lives only in
`threads/spitballs/01-the-currency.md` as *candidate, not-yet-proposed* canon,
and the walk server does not surface it — so it is NOT answerable by walking and
is deliberately NOT a question here. Every question below is answerable purely
from the walk server's own `look/go/talk_to/do/work` output, and cites where.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# THE FIELD QUESTIONS. Each is answerable only by exploring the walk world.
#   expect: list of keyword GROUPS. A group matches if ANY of its synonyms is a
#           case-insensitive substring of the answer. Full credit needs every
#           group; partial credit is the fraction of groups matched.
#   grounded: engagement signals (place / action / person substrings) that count
#           as "did the exploration this answer requires" for the shaping term.
#   citation: the repository file(s) a reader can check the truth against.
# Extend by appending a dict with the same shape — nothing else needs to change.
# ---------------------------------------------------------------------------

FIELD_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "prompt": (
            "Sit the 3 a.m. fever-watch, then talk to the people who live it. "
            "What is that night care-shift called, in what ledger is it written, "
            "and is it paid as a wage?"
        ),
        "expect": [
            ["deep hour", "deep-hour", "deep hours"],
            ["rest-ledger", "rest ledger", "ledger"],
            ["not a wage", "no wage", "not paid", "debt", "reputation", "gift", "unpaid"],
        ],
        "citation": (
            "CANON.md ('The rest-ledger'); threads/chains/01-deep-hours.md; "
            "walk do('sit a deep hour')"
        ),
        "explanation": (
            "The shift is a 'deep hour' — the 3 a.m. fever-watch — written into the "
            "rest-ledger. It is not a wage: it records a debt the neighbourhood carries "
            "and owes back in daylight, never the worth of the one who gave it "
            "(Fureai Kippu / ILO care-labour lineage)."
        ),
        "grounded": {
            "places": ["the grown building off yesler", "the central district"],
            "actions": ["deep hour"],
            "people": ["persimmon", "tuesday"],
        },
    },
    {
        "id": "q2",
        "prompt": (
            "The seawall drops daylight through glass blocks set in the sidewalk. "
            "For whom is the light dropped, and what does the season's stencilled "
            "count measure?"
        ),
        "expect": [
            ["salmon", "chinook"],
            ["glass block", "glass-block", "sidewalk", "daylight", "light", "corridor"],
        ],
        "citation": (
            "CANON.md ('Ecology'); research/food-and-marine.md; "
            "walk look('the seawall') and work('the seawall')"
        ),
        "explanation": (
            "The daylight drops through the glass-block sidewalk to the young Chinook "
            "salmon running the lit nearshore corridor below; the stencilled count is "
            "the co-managed salmon count (the sea is restored, not healed)."
        ),
        "grounded": {
            "places": ["the seawall"],
            "actions": ["seawall"],
            "people": [],
        },
    },
    {
        "id": "q3",
        "prompt": (
            "Find the House of Marrow. Who is its house-mother, and what kind of "
            "unit is a 'House' in this world?"
        ),
        "expect": [
            ["tuesday marrow", "tuesday"],
            ["house", "kinship", "chosen family", "care", "fourteen", "hungry or unwatched"],
        ],
        "citation": (
            "CANON.md ('Houses'); threads/the-band-girl.md; "
            "walk look('the House of Marrow') and talk_to('Tuesday Marrow')"
        ),
        "explanation": (
            "Tuesday Marrow keeps the House of Marrow. A House is the primary "
            "kinship-and-care unit — commons-registered chosen family (ballroom "
            "lineage) — here fourteen people under a rule that nobody in it goes "
            "hungry or unwatched."
        ),
        "grounded": {
            "places": ["the house of marrow"],
            "actions": [],
            "people": ["tuesday", "band girl", "dryland"],
        },
    },
    {
        "id": "q4",
        "prompt": (
            "Carry a thread on the Weave, or ask the carrier about it. What does "
            "this world use instead of the internet, and why can 'reach' not be "
            "ranked or sold on it?"
        ),
        "expect": [
            ["weave"],
            [
                "not computable", "cannot be computed", "can't be computed",
                "no node", "relays forget", "forgetful", "delay-tolerant",
                "store-and-forward", "no node holds", "not ranked", "cannot be sold",
            ],
        ],
        "citation": (
            "CANON.md ('The Weave'); research/the-weave.md; "
            "walk do('carry a thread') and talk_to('Hale')"
        ),
        "explanation": (
            "The Weave — Delay-Tolerant Networking (store-and-forward Bundle Protocol) "
            "with mesh radio. Because relays are forgetful and no node holds the whole "
            "graph, reach is literally not computable, so there is nothing to rank and "
            "nothing to sell."
        ),
        "grounded": {
            "places": ["the north harbor", "the outer islands"],
            "actions": ["carry"],
            "people": ["hale"],
        },
    },
    {
        "id": "q5",
        "prompt": (
            "Stand at the Hard-Choices wall. When care is singular and cannot reach "
            "everyone, how does the choice get made, and what 1962 Seattle committee "
            "is the protocol built to never become again?"
        ),
        "expect": [
            ["drawn lot", "a lot", "lottery", "public", "revisable", "no quality-of-life", "forbid ranking"],
            ["god committee", "1962", "dialysis", "swedish"],
        ],
        "citation": (
            "CANON.md ('When the machine can't save everyone'); "
            "research/scarcity-and-hard-tradeoffs.md; "
            "walk do('stand at the Hard-Choices wall')"
        ),
        "explanation": (
            "The Hard-Choices Protocol: public, revisable rules that forbid ranking a "
            "person's worth, with a drawn lot breaking the remaining ties and a wall of "
            "the names it could not save. Its founding warning is the real 1962 Seattle "
            "'God Committee' that chose who got the first scarce dialysis by secret "
            "judgments of social worth."
        ),
        "grounded": {
            "places": ["the grown building off yesler", "the central district"],
            "actions": ["hard-choices", "hard choices"],
            "people": [],
        },
    },
]

# Reward weighting: answer correctness dominates; exploration is light shaping.
ANSWER_WEIGHT = 0.85
EXPLORATION_WEIGHT = 0.15
DEFAULT_STEP_BUDGET = 40


# ---------------------------------------------------------------------------
# Grading — pure functions, no I/O, reusable by any framework.
# ---------------------------------------------------------------------------


def _group_matched(answer_lc: str, group: List[str]) -> Optional[str]:
    for syn in group:
        if syn.lower() in answer_lc:
            return syn
    return None


def grade_question(question: Dict[str, Any], answer: Optional[str]) -> Dict[str, Any]:
    """Grade one answer against a question's expected keyword groups."""
    answer = answer or ""
    answer_lc = answer.lower()
    matched: List[str] = []
    missed: List[List[str]] = []
    for group in question["expect"]:
        hit = _group_matched(answer_lc, group)
        if hit is not None:
            matched.append(hit)
        else:
            missed.append(group)
    total = len(question["expect"])
    score = (total - len(missed)) / total if total else 0.0
    return {
        "id": question["id"],
        "given": answer,
        "score": round(score, 4),
        "matched": matched,
        "missed": missed,
        "citation": question["citation"],
        "explanation": question["explanation"],
    }


def grade_answers(
    answers: Dict[str, str],
    questions: List[Dict[str, Any]] = FIELD_QUESTIONS,
    engaged: Optional[set] = None,
) -> Dict[str, Any]:
    """Grade all answers. Returns a full report with a blended reward.

    Args:
        answers: mapping of question id -> submitted answer text.
        questions: the question set (defaults to FIELD_QUESTIONS).
        engaged: set of engagement signals (lowercased place/action/person
            substrings) the agent hit this episode, for the exploration term.
    """
    engaged = engaged or set()
    per_question = [grade_question(q, answers.get(q["id"])) for q in questions]
    answer_score = (
        sum(r["score"] for r in per_question) / len(per_question)
        if per_question
        else 0.0
    )

    # Exploration coverage: fraction of questions whose grounded place / action /
    # person was actually engaged this episode (map/where readouts don't count).
    covered = 0
    coverage_detail: Dict[str, bool] = {}
    for q in questions:
        signals = (
            q["grounded"].get("places", [])
            + q["grounded"].get("actions", [])
            + q["grounded"].get("people", [])
        )
        hit = any(_signal_engaged(sig, engaged) for sig in signals)
        coverage_detail[q["id"]] = hit
        covered += 1 if hit else 0
    exploration = covered / len(questions) if questions else 0.0

    reward = ANSWER_WEIGHT * answer_score + EXPLORATION_WEIGHT * exploration
    return {
        "reward": round(reward, 4),
        "answer_score": round(answer_score, 4),
        "exploration": round(exploration, 4),
        "answered": sorted(answers.keys()),
        "num_questions": len(questions),
        "per_question": per_question,
        "coverage": coverage_detail,
    }


def _signal_engaged(signal: str, engaged: set) -> bool:
    # Word-boundary match so a grounded signal like "wall" does NOT match
    # "seawall", and short place/person tokens don't over-credit exploration.
    sig = signal.lower().strip()
    if not sig:
        return False
    pattern = re.compile(r"\b" + re.escape(sig) + r"\b")
    return any(pattern.search(e) for e in engaged)


def render_report(report: Dict[str, Any]) -> str:
    """Human/agent-readable grading, citing the source file for each answer."""
    lines: List[str] = []
    lines.append("# Field report — the walk-and-learn verifier")
    lines.append(
        f"Reward **{report['reward']}**  "
        f"(answers {report['answer_score']} x{ANSWER_WEIGHT} + "
        f"exploration {report['exploration']} x{EXPLORATION_WEIGHT})."
    )
    for r in report["per_question"]:
        verdict = "correct" if r["score"] >= 1.0 else (
            "partial" if r["score"] > 0 else "missed"
        )
        lines.append(f"\n## {r['id']} — {verdict} ({r['score']})")
        lines.append(f"You answered: {r['given'] or '(no answer)'}")
        if r["matched"]:
            lines.append(f"Right: matched {', '.join(repr(m) for m in r['matched'])}.")
        if r["missed"]:
            need = "; ".join("one of " + repr(g) for g in r["missed"])
            lines.append(f"Missed: still need {need}.")
        lines.append(f"Grounded in: {r['citation']}")
        if r["score"] < 1.0:
            lines.append(f"The world's answer: {r['explanation']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Action parsing — a single free-text command per step.
# ---------------------------------------------------------------------------

# Map an action verb to the MCP tool + the argument name the walk server expects.
_WORLD_TOOLS = {
    "look": ("look", None),
    "map": ("map", None),
    "where": ("where", None),
    "join": ("join", None),
    "go": ("go", "place"),
    "talk_to": ("talk_to", "person"),
    "talk": ("talk_to", "person"),
    "do": ("do", "action"),
    "work": ("work", "shift"),
}


@dataclass
class ParsedAction:
    kind: str  # 'world' | 'answer' | 'submit' | 'unknown'
    tool: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    qid: Optional[str] = None
    text: Optional[str] = None
    raw: str = ""


def parse_action(command: str) -> ParsedAction:
    """Parse one command string into a structured action.

    Grammar (case-insensitive verbs):
        look | map | where | join
        go <place>            talk_to <person>       do <action>     work <shift>
        answer <qid> <text>   answer <qid>: <text>   submit
    """
    raw = (command or "").strip()
    if not raw:
        return ParsedAction(kind="unknown", raw=raw)
    parts = raw.split(None, 1)
    verb = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    # "talk to X" -> normalize to talk_to
    if verb == "talk" and rest.lower().startswith("to "):
        rest = rest[3:].strip()

    if verb == "submit":
        return ParsedAction(kind="submit", raw=raw)

    if verb == "answer":
        m = re.match(r"^(?P<qid>[A-Za-z]?\d+)\s*:?\s*(?P<text>.*)$", rest, re.DOTALL)
        if not m or not m.group("text").strip():
            return ParsedAction(kind="unknown", raw=raw)
        qid = m.group("qid").lower()
        if not qid.startswith("q"):
            qid = "q" + qid
        return ParsedAction(kind="answer", qid=qid, text=m.group("text").strip(), raw=raw)

    if verb in _WORLD_TOOLS:
        tool, arg_name = _WORLD_TOOLS[verb]
        if arg_name is None:
            return ParsedAction(kind="world", tool=tool, args={}, raw=raw)
        if not rest:
            return ParsedAction(kind="unknown", raw=raw)
        return ParsedAction(kind="world", tool=tool, args={arg_name: rest}, raw=raw)

    return ParsedAction(kind="unknown", raw=raw)


# ---------------------------------------------------------------------------
# The episode engine — owns the bridge, tracks exploration, records answers,
# and finalizes. Both adapters wrap this so the task logic lives in one place.
# ---------------------------------------------------------------------------


@dataclass
class StepOutcome:
    text: str
    reward: float
    done: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class WalkEpisode:
    """One walk-and-learn episode over a walk MCP server.

    Args:
        bridge_factory: a zero-arg callable returning a *started* MCPWalkBridge.
            reset() calls it to (re)launch the world so the episode truly starts
            fresh at the seawall.
        questions: the field-question set (defaults to FIELD_QUESTIONS).
        step_budget: hard cap on steps; the episode finalizes when hit.
    """

    def __init__(
        self,
        bridge_factory: Callable[[], Any],
        questions: List[Dict[str, Any]] = FIELD_QUESTIONS,
        step_budget: int = DEFAULT_STEP_BUDGET,
    ) -> None:
        self._factory = bridge_factory
        self._questions = questions
        self._budget = step_budget
        self._bridge = None
        self._reset_tracking()

    def _reset_tracking(self) -> None:
        self.steps = 0
        self.place: Optional[str] = None
        self.answers: Dict[str, str] = {}
        self.engaged: set = set()
        self.done = False
        self.reward = 0.0
        self.final_report: Optional[Dict[str, Any]] = None

    # -- lifecycle ------------------------------------------------------------

    def reset(self) -> StepOutcome:
        if self._bridge is not None:
            self._bridge.close()
        self._bridge = self._factory()
        self._reset_tracking()
        text = self._bridge.call("look")
        self._track_world("look", {}, text)
        goal = self._goal_text()
        return StepOutcome(
            text=goal + "\n\n" + text,
            reward=0.0,
            done=False,
            metadata=self._meta(),
        )

    def close(self) -> None:
        if self._bridge is not None:
            self._bridge.close()
            self._bridge = None

    # -- stepping -------------------------------------------------------------

    def step(self, command: str) -> StepOutcome:
        if self.done:
            return StepOutcome(
                text="The episode is over. Call reset() to walk again.",
                reward=0.0,
                done=True,
                metadata=self._meta(),
            )
        if self._bridge is None:
            raise RuntimeError("episode not started; call reset() first")

        self.steps += 1
        action = parse_action(command)

        if action.kind == "world":
            text = self._bridge.call(action.tool, action.args)
            self._track_world(action.tool, action.args, text)
            return self._maybe_budget(StepOutcome(text, 0.0, False, self._meta()))

        if action.kind == "answer":
            if action.qid not in {q["id"] for q in self._questions}:
                valid = ", ".join(q["id"] for q in self._questions)
                return self._maybe_budget(
                    StepOutcome(
                        f"No such question '{action.qid}'. Questions are: {valid}.",
                        0.0, False, self._meta(),
                    )
                )
            self.answers[action.qid] = action.text
            remaining = [q["id"] for q in self._questions if q["id"] not in self.answers]
            if not remaining:
                return self._finalize("All questions answered.")
            ack = (
                f"Recorded answer for {action.qid}. "
                f"Answered {len(self.answers)}/{len(self._questions)}. "
                f"Still open: {', '.join(remaining)}."
            )
            return self._maybe_budget(StepOutcome(ack, 0.0, False, self._meta()))

        if action.kind == "submit":
            return self._finalize("Submitted.")

        # unknown
        help_text = (
            f"Unrecognized command: {command!r}. Try one of: "
            "look; map; where; go <place>; talk_to <person>; do <action>; "
            "work <shift>; answer <qid> <text>; submit."
        )
        return self._maybe_budget(StepOutcome(help_text, 0.0, False, self._meta()))

    # -- internals ------------------------------------------------------------

    def _maybe_budget(self, outcome: StepOutcome) -> StepOutcome:
        if not self.done and self.steps >= self._budget:
            return self._finalize(f"Step budget ({self._budget}) reached.")
        return outcome

    def _finalize(self, reason: str) -> StepOutcome:
        report = grade_answers(self.answers, self._questions, self.engaged)
        self.final_report = report
        self.reward = report["reward"]
        self.done = True
        text = f"{reason}\n\n" + render_report(report)
        meta = self._meta()
        meta["report"] = report
        return StepOutcome(text=text, reward=self.reward, done=True, metadata=meta)

    def _track_world(self, tool: str, args: Dict[str, Any], text: str) -> None:
        """Record genuine world engagement (not map/where readouts) for shaping."""
        # Current place, parsed from a place header "# <name>" (look/go only).
        if tool in ("look", "go"):
            m = re.search(r"^#\s+(the [^\n]+)$", text, re.MULTILINE)
            if m:
                place = m.group(1).strip()
                # Only a real arrival, not the "# No road ..." honest refusal.
                if not place.lower().startswith("no road"):
                    self.place = place
                    self.engaged.add(place.lower())
        if tool == "talk_to":
            failed = any(
                s in text
                for s in ("isn't here", "No one called", "Say who you mean")
            )
            person = str(args.get("person", "")).lower().strip()
            if person and not failed:
                self.engaged.add(person)
        if tool in ("do", "work"):
            m = re.search(r"^#\s+You (?:do|work):\s*(.+)$", text, re.MULTILINE)
            if m:
                self.engaged.add(m.group(1).strip().lower())

    def _goal_text(self) -> str:
        qs = "\n".join(f"- {q['id']}: {q['prompt']}" for q in self._questions)
        return (
            "# Goal — walk and learn\n"
            "You have arrived by water in The Reality Next Door. Explore it — "
            "`go` between places, `talk_to` the people, `do` the work — then answer "
            "these grounded field questions with `answer <qid> <text>`, and `submit` "
            "(or answer them all). You cannot answer them from here; you have to walk.\n\n"
            f"{qs}\n\n"
            f"Step budget: {self._budget}."
        )

    def _meta(self) -> Dict[str, Any]:
        return {
            "place": self.place,
            "steps": self.steps,
            "answered": sorted(self.answers.keys()),
            "questions_remaining": [
                q["id"] for q in self._questions if q["id"] not in self.answers
            ],
            "num_questions": len(self._questions),
        }
