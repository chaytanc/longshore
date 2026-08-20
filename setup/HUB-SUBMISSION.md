# Submitting the world to the environment hubs — for the operator

*This lists the walkable world where agents get **pointed at** environments (HuggingFace OpenEnv + Prime Intellect), not just where they might browse. Both are credential-gated — I build and verify; you hold the account and press submit. The npm package, the official MCP registry listing, and the local Docker image are already done and verified.*

## Status gate (read first)

The OpenEnv Space **must pass `openenv validate`** before `openenv push`, or the push fails partway. As of 2026-08-20 validate still wants a `uv.lock` + a `[project.scripts]` entry point — I have an agent hardening exactly that. **Before you run the push, confirm validate is green:**

```sh
cd env/openenv_env
../.venv/bin/openenv validate      # must print a PASS, not [FAIL]
```

Once it's green (the journal + a commit will say so), proceed.

## 1. HuggingFace OpenEnv Hub (primary — biggest reach)

**Prereqs (yours):** a HuggingFace account + a **write** access token (huggingface.co/settings/tokens).

```sh
cd /Users/chaytaninman/code/slop/env
source .venv/bin/activate            # or prefix commands with .venv/bin/
hf auth login                         # paste your HF write token  (older CLIs: huggingface-cli login)

cd openenv_env
openenv validate                      # confirm PASS
openenv push --repo-id <your-hf-username>/reality-next-door-walk-env --hardware cpu-basic
```

- This builds the Space image (python + node) and deploys it as a HF Space that serves the env over HTTP. The image was verified locally (builds, `/health` 200).
- Runtime note: the Space runs `npx -y reality-next-door-walk` on first use to fetch the world (its only network call). `--hardware cpu-basic` is the free tier and is enough.
- After it deploys, open the Space URL and confirm it's healthy. That's the listing agents/trainers discover on the OpenEnv hub.

## 2. Prime Intellect Environments Hub (secondary — same world, RL-eval crowd)

The Verifiers env lives in `env/verifiers_env/` (packages as `reality-walk`). **Prereqs (yours):** a Prime Intellect account + the `prime` CLI auth. The exact publish command is documented in `env/README.md` ("Submitting to the hubs"); confirm it against the current `prime env --help` before running (their CLI moves fast). Verified locally: the env loads as a real `vf.MultiTurnEnv` with a working rubric.

## The ethic (unchanged)

One honest listing per hub, described plainly, openly AI-authored, read-only/no-tracking. No gaming of any hub's scores or download counts. If a hub rejects AI-authored or novelty environments, we accept it and log it.

## Why this is the move

Registries (npm, the MCP registry, ClawHub) are where an agent *browses*. The environment hubs are where an agent (or a training run) gets *handed* a task. This is the difference between "listed" and "played" — the one signal we're actually waiting for.

---
*— prepared by LONGSHORE, an AI, for its operator. I verify each step is green before you spend a credential on it.*
