---
title: Reality Next Door — Walk Env
emoji: 🌊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
license: mit
---

# reality-next-door-walk-env (OpenEnv)

An **OpenEnv** agent environment: a "walk and learn" episode over the cited,
walkable world **The Reality Next Door**. It bridges to the published
[`reality-next-door-walk`](https://www.npmjs.com/package/reality-next-door-walk)
MCP server as a stdio subprocess and maps `reset()` / `step()` / `close()` onto
real MCP tool calls, so the world is never reimplemented (one source of truth).

The agent is asked 5 grounded field questions it can only answer by walking,
talking, and doing; the reward grades answers against canon keywords (with
citations) plus light exploration shaping. Full design, both adapters, and the
ethic: see the parent [`../README.md`](../README.md).

## Validate & deploy

```sh
cd openenv_env
openenv validate                 # structure + deployment readiness
# type your HF username literally, no angle brackets:
openenv push --repo-id YOURNAME/reality-next-door-walk-env --hardware cpu-basic --exclude .hfignore
```

`push` stages this directory's *contents* to the Space build root, so everything
the image needs is here: the FastAPI server (`server/app.py`, addressed flat as
`server.app:app`), the OpenEnv adapter, and the **vendored** `reality_walk` core.

## A note on the vendored core

`reality_walk/` here is a byte-for-byte copy of the canonical shared core at
[`../reality_walk/`](../reality_walk/) (the bridge + task engine). It is vendored
because `openenv push` packages only this directory, so a sibling import would
not survive deployment. A drift guard (`../tests/test_vendored_core.py`) fails CI
if the copy ever diverges from the canonical source.

## Run the image locally

```sh
docker build -f Dockerfile -t reality-walk-env .
docker run -p 8000:8000 reality-walk-env
curl localhost:8000/health        # -> {"status":"healthy"}
```

The image includes Node.js because the world is a Node MCP server launched via
`npx`. That first `npx` fetch is the only network access; the walk server itself
makes none.

---
*— built and signed by **LONGSHORE**, an AI, openly. Operator holds the
credentials and runs `openenv push`.*
