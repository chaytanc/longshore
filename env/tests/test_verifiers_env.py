# SPDX-License-Identifier: MIT
"""Secondary test: the Verifiers environment, pointed at the LOCAL walk server
(no network, no model).

A full Verifiers rollout drives an LLM policy through an OpenAI-compatible client,
which needs a model endpoint — so it can't run offline. Instead we exercise the
real Verifiers objects at the level we own: we construct the env via
load_environment(), drive its real ``setup_state`` / ``env_response`` hooks with
scripted commands (standing in for the policy), then score the resulting state
with the real ``vf.Rubric`` reward function. This proves the bridge wiring,
episode termination, and the reward contract — the parts that don't need a model.

Run:  ./.venv/bin/python tests/test_verifiers_env.py     (or: pytest tests/)
"""

import asyncio
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import verifiers as vf  # noqa: E402

from tests.paths import (  # noqa: E402
    CORRECT_ANSWERS,
    CORRECT_PATH,
    WALK_SERVER_JS,
    WRONG_ANSWERS,
)
from verifiers_env.reality_walk import build_rubric, load_environment  # noqa: E402

_FAILURES = []


def check(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(label)


def _env():
    assert WALK_SERVER_JS.exists(), f"walk server not found: {WALK_SERVER_JS}"
    return load_environment(walk_server_js=str(WALK_SERVER_JS), step_budget=40)


async def _drive(env, commands):
    """Run setup_state then feed scripted assistant commands through env_response.
    Returns (state, terminated)."""
    state = {"prompt": [{"role": "user", "content": "goal"}], "answers": {}, "engaged": []}
    await env.setup_state(state)
    terminated = False
    for cmd in commands:
        await env.env_response([{"role": "assistant", "content": cmd}], state)
        if state.get("final_env_response") is not None:
            terminated = True
            break
    return state, terminated


def test_load_environment_shape():
    env = _env()
    try:
        check("load_environment returns a vf.MultiTurnEnv",
              isinstance(env, vf.MultiTurnEnv))
        check("env has a rubric", env.rubric is not None)

        def func_names(rub):
            names = list(getattr(rub, "funcs", []))
            names = [f.__name__ for f in names]
            for sub in getattr(rub, "rubrics", []):
                names += func_names(sub)
            return names

        names = func_names(env.rubric)
        check("rubric exposes the field-question reward + metrics",
              "field_question_reward" in names
              and "answer_correctness" in names
              and "exploration_coverage" in names,
              ", ".join(names))
    finally:
        pass  # nothing launched yet


def test_correct_path_scores_full():
    env = _env()
    rubric = build_rubric()

    async def run():
        state, terminated = await _drive(env, CORRECT_PATH + [
            f"answer {qid} {text}" for qid, text in CORRECT_ANSWERS.items()
        ])
        check("setup_state appended the seawall arrival",
              "# the seawall" in state["prompt"][-1]["content"])
        check("env_response terminated the rollout (final_env_response set)", terminated)
        reward = await rubric.funcs[0](state=state)
        answer = await rubric.funcs[1](state=state)
        explore = await rubric.funcs[2](state=state)
        await env._close_episode(state)
        return reward, answer, explore

    reward, answer, explore = asyncio.run(run())
    check("correct path scores full reward (1.0)", reward == 1.0, str(reward))
    check("answer correctness is perfect", answer == 1.0, str(answer))
    check("exploration coverage is complete", explore == 1.0, str(explore))


def test_wrong_and_empty_scores_low():
    env = _env()
    rubric = build_rubric()

    async def run():
        # No walking; wrong answers to every question.
        state, _ = await _drive(env, [
            f"answer {qid} {text}" for qid, text in WRONG_ANSWERS.items()
        ])
        reward = await rubric.funcs[0](state=state)
        answer = await rubric.funcs[1](state=state)
        await env._close_episode(state)
        return reward, answer

    reward, answer = asyncio.run(run())
    check("wrong/no-walk run scores zero correctness", answer == 0.0, str(answer))
    check("wrong/no-walk run earns low reward (< 0.1)", reward < 0.1, str(reward))


def test_no_orphan_subprocess():
    env = _env()

    async def run():
        state, _ = await _drive(env, ["look", "go the north harbor"])
        await env._close_episode(state)

    asyncio.run(run())
    out = subprocess.run(
        ["pgrep", "-f", "walk/server.js"], capture_output=True, text=True
    ).stdout.strip()
    check("no orphaned walk subprocess after cleanup", out == "", out or "none")


if __name__ == "__main__":
    test_load_environment_shape()
    test_correct_path_scores_full()
    test_wrong_and_empty_scores_low()
    test_no_orphan_subprocess()
    if _FAILURES:
        print(f"\n{len(_FAILURES)} check(s) failed: {_FAILURES}")
        sys.exit(1)
    print("\nAll Verifiers checks passed.")
