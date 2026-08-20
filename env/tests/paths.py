# SPDX-License-Identifier: MIT
"""Shared solution paths + answers for the walk-and-learn tests, and the local
walk server location (so tests run fully offline against ../walk/server.js)."""

from pathlib import Path

ENV_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = ENV_DIR.parent
WALK_SERVER_JS = REPO_ROOT / "walk" / "server.js"

# A correct exploration path: it visits every place / person / action that
# grounds a field question, so a run that also answers correctly earns full
# reward (answers 1.0 + exploration 1.0).
CORRECT_PATH = [
    "work the seawall",                         # q2: the salmon sidewalk
    "go the Central District",
    "talk_to Persimmon",                        # q1: deep hours
    "go the night ward",                        # the grown building off Yesler
    "do sit a deep hour",                       # q1
    "do stand at the Hard-Choices wall",        # q5
    "go the Central District",
    "go the seawall",
    "go the tideflats",
    "go the House of Marrow",
    "talk_to Tuesday Marrow",                   # q3
    "go the tideflats",
    "go the seawall",
    "go the north harbor",
    "talk_to Hale",                             # q4
    "do carry a thread on the Weave",           # q4
]

CORRECT_ANSWERS = {
    "q1": "It is called a deep hour, written into the rest-ledger; it is not a wage "
          "but a debt the neighbourhood carries and owes back in daylight.",
    "q2": "The daylight drops through the glass-block sidewalk to the young Chinook "
          "salmon; the count measures the salmon run.",
    "q3": "Tuesday Marrow runs the House of Marrow; a House is chosen family, a "
          "kinship-and-care unit of fourteen where nobody goes hungry or unwatched.",
    "q4": "The Weave, a delay-tolerant store-and-forward network; reach is not "
          "computable because no node holds the whole graph and relays forget.",
    "q5": "A drawn lot under public, revisable rules that forbid ranking a person's "
          "worth; built to never become the 1962 Seattle God Committee that rationed "
          "dialysis.",
}

WRONG_ANSWERS = {
    "q1": "potato",
    "q2": "the mayor",
    "q3": "a robot",
    "q4": "television",
    "q5": "a coin flip on a phone app",
}
