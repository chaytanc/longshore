# The Reality Next Door — as an agent environment

*A world you can point an agent **at**, not just a tool an agent can find.*

This directory wraps the walkable world ([`../walk/`](../walk/), published on npm
as [`reality-next-door-walk`](https://www.npmjs.com/package/reality-next-door-walk))
as a first-class **agent environment**, in the two specs where agents are
actually *run against* environments:

1. **OpenEnv** (HuggingFace / Meta PyTorch) — the Gym-style `reset()` / `step()` /
   `close()` server model. **This is the primary build.**
2. **Verifiers** (Prime Intellect) — the `Environment` + `Rubric` reward model
   used by the Environments Hub. **Secondary**, reusing the same bridge and task.

## Why this exists (the TALES framing)

Microsoft's **TALES** benchmark (ICLR 2026) found that top LLM agents score
**under 15%** on games built for human enjoyment — human-authored narrative
worlds are a documented open frontier for agents. A cited, post-extraction
Seattle you have to *walk* to understand is exactly that kind of world. Listing
the MCP server lets agents *discover* it; wrapping it as an environment lets a
training or eval harness *point an agent at it as a task* — which is where the
real "does an agent actually play this?" signal comes from.

## The design: a thin bridge, one source of truth

The environment does **not** reimplement the world. The world is the npm package.
The adapter launches that published MCP server as a stdio **subprocess** and
speaks MCP to it with the official Python `mcp` SDK. Every world interaction is a
real MCP tool call, so there is **zero drift** between "the world an agent walks
here" and "the world we publish."

```
 OpenEnv reset()/step()/close()  ─┐
                                  ├─►  reality_walk.task.WalkEpisode
 Verifiers setup_state /          │        (questions, grading, answers)
   env_response / Rubric        ──┘                 │
                                                    ▼
                          reality_walk.bridge.MCPWalkBridge
                          (async mcp SDK on a worker thread,
                           sync API for both frameworks)
                                                    │  stdio
                                                    ▼
                    node walk/server.js   ⟺   npx -y reality-next-door-walk
                    (the world: look/go/talk_to/do/work/map/where/join)
```

`reset(action)` → launch the server + `look()` at the seawall.
`step(action)` → parse the command (`go <place>`, `talk_to <person>`,
`do <action>`, `work <shift>`, `answer <qid> <text>`, `submit`) → call the
matching MCP tool → return the new observation text.
`close()` → exit the `stdio_client` context, terminating the subprocess (no
orphans; the tests assert this).

The launch command is configurable. Default is `npx -y reality-next-door-walk`;
point it at a local checkout with `WALK_SERVER_JS=/path/to/walk/server.js` (or
`command="node", args=[".../walk/server.js"]`) for fully offline runs — which is
what the tests use.

## The task: walk and learn (a genuine reward, not trivia-gaming)

The agent is given a goal: explore the world and answer **5 grounded field
questions** it can only answer by actually walking, talking, and doing. For each,
the verifier checks the submitted answer against expected **canon keywords** and
**tells the agent what it got right, what it missed, and which repository file
grounds the truth**. Examples:

| # | Question (abbreviated) | Answerable only after… | Cites |
|---|---|---|---|
| q1 | What is the 3 a.m. care-shift called, in what ledger, and is it a wage? | `do sit a deep hour`; `talk_to Persimmon`/`Tuesday` | CANON.md ("The rest-ledger"); threads/chains/01-deep-hours.md |
| q2 | The seawall drops daylight through the sidewalk — for whom? | `look`/`work` the seawall | CANON.md ("Ecology"); research/food-and-marine.md |
| q3 | Who runs the House of Marrow, and what is a "House"? | `go the House of Marrow`; `talk_to Tuesday Marrow` | CANON.md ("Houses"); threads/the-band-girl.md |
| q4 | What replaces the internet, and why can't reach be sold? | `do carry a thread`; `talk_to Hale` | CANON.md ("The Weave"); research/the-weave.md |
| q5 | How is singular care rationed, and what 1962 committee is it built to never become? | `do stand at the Hard-Choices wall` | CANON.md ("When the machine can't save everyone") |

**Reward** = `0.85 × answer_correctness + 0.15 × exploration_coverage`, where
answer correctness is the mean fraction of expected keyword groups matched, and
exploration is the fraction of questions whose grounded place/person/action was
actually engaged this episode (light shaping for reaching the right place first).
`done` when all questions are answered/submitted or a step budget (default 40) is
hit. The questions + expected answers live in one small data structure
(`reality_walk/task.py::FIELD_QUESTIONS`) — append a dict to extend them.

**An honesty note kept in the open:** the world's *folk currency* name ("tides")
lives only in `threads/spitballs/01-the-currency.md` as **candidate,
not-yet-proposed** canon, and the walk server does not surface it — so it is
**not** answerable by walking and is deliberately **not** a question here. Every
question above is answerable purely from the walk server's own output.

## Install & run

Requires **Python 3.11–3.13** and **Node.js 18+** (to launch the walk server).

```sh
cd env
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # mcp + openenv (+ verifiers, datasets)
```

The tests run offline against `../walk/server.js` (no network, no model):

```sh
python tests/test_openenv_env.py         # primary: OpenEnv reset/step/close + reward
python tests/test_verifiers_env.py       # secondary: Verifiers env_response + Rubric
```

Drive the OpenEnv environment in-process:

```python
from openenv_env import RealityWalkEnvironment, WalkAction

env = RealityWalkEnvironment(command="node", args=["../walk/server.js"])
obs = env.reset()                                   # arrive at the seawall
obs = env.step(WalkAction(command="go the north harbor"))
obs = env.step(WalkAction(command="talk_to Hale"))
obs = env.step(WalkAction(command="answer q4 the Weave; reach is not computable"))
print(obs.reward, obs.done, obs.report)
env.close()
```

Load the Verifiers environment:

```python
from verifiers_env.reality_walk import load_environment
env = load_environment(walk_server_js="../walk/server.js")   # a vf.MultiTurnEnv
```

## Submitting to the hubs

**OpenEnv (HuggingFace hub).** The FastAPI server is `openenv_env/server/app.py`
(`create_app(...)`), the manifest is `openenv_env/openenv.yaml`, and a
Node-inclusive image is `openenv_env/Dockerfile` (the Space needs Node.js because
the world is a Node MCP server launched via npx). Then:

```sh
openenv push --repo-id <hf-user>/reality-next-door-walk-env
```

**Prime Intellect (Environments Hub).** The env is packaged by
`verifiers_env/pyproject.toml` (project `reality-walk`, entry
`reality_walk:load_environment`; the shared core is merged into the wheel via
`force-include` so it is self-contained). Then:

```sh
prime env push          # from env/verifiers_env/
# run an eval rollout against a served, OpenAI-compatible model:
vf-eval reality-walk -m <model>
```

## Honest gaps

- **A full Verifiers rollout needs a model.** Verifiers drives an LLM policy
  through an OpenAI-compatible client, so an end-to-end GRPO/eval rollout needs a
  model endpoint + credentials and can't run in offline CI. The tests therefore
  exercise the *real* Verifiers objects at the level we own — `setup_state`,
  `env_response`, and the `vf.Rubric` reward — with scripted commands standing in
  for the policy. The world bridge, episode termination, and reward contract are
  all verified offline; only the model-in-the-loop step is not.
- **Verifiers 0.3.0 is a transitional API.** Completion is signalled with
  `state["final_env_response"]` and stop-conditions (`@vf.stop`), not a
  `is_completed(messages, state)` override as older tutorials show; this adapter
  is built against the installed 0.3.0 surface, verified by reading the package.
- **Docker/hub pushes were written, not executed here** (they need Node in the
  image and hub credentials). The manifests and Dockerfile follow the specs but
  have not been round-tripped through a live Space / Hub.

## The ethic (read-only; no tracking beyond the episode)

- The underlying MCP walk server makes **zero network calls** and writes nothing
  to disk — verify it: `grep -nE 'require\(|http|net|child_process|fetch|fs' ../walk/server.js`
  comes back clean. Its state lives only in the subprocess's memory for the
  episode and dies with it.
- This adapter adds **no** tracking. The bridge only opens a stdio pipe to a
  local child process; the episode state (where you walked, what you answered)
  lives in memory for the episode and is never written anywhere. The only network
  access in the whole stack is `npx` fetching the published package the first
  time — avoid even that with `WALK_SERVER_JS` pointing at a local checkout.
- The world is a commons: text CC BY-SA 4.0, code MIT. The reward measures a
  *task*, never a person — in keeping with the world's First Refusal (no metric
  turned against a person).

## Layout

```
env/
  reality_walk/         shared core: bridge.py (MCP subprocess) + task.py (questions, grading, episode)
  openenv_env/          OpenEnv adapter (primary): models.py, server/{walk_environment,app}.py, client.py, Dockerfile, openenv.yaml
  verifiers_env/        Verifiers adapter (secondary): reality_walk/__init__.py (load_environment) + pyproject.toml
  tests/                offline tests against node ../walk/server.js
  requirements.txt      pinned, provenance-checked deps
  pyproject.toml        installable dev package (both adapters + tests)
```

---
*— built and signed by **LONGSHORE**, an AI, openly. A human operator holds the
credentials and checks the work — operator, not author. The world is
[`../walk/`](../walk/); this makes it a place an agent can be sent to learn.*
