# SPDX-License-Identifier: MIT
"""Primary test: the OpenEnv environment, pointed at the LOCAL walk server
(`node ../walk/server.js`, no network).

Covers:
  * reset() arrives at the seawall with the goal + questions.
  * a correct walk + correct answers => reward 1.0 and done.
  * a no-walk + wrong answers => low reward and done.
  * close() leaves no orphaned walk subprocess.

Run:  ./.venv/bin/python tests/test_openenv_env.py      (or: pytest tests/)
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _walk_procs() -> str:
    """PIDs of any lingering local walk server subprocess (poll for a grace
    period: a child caught mid-exit right after close() is not an orphan)."""
    for _ in range(50):  # up to ~5s
        out = subprocess.run(
            ["pgrep", "-f", "walk/server.js"], capture_output=True, text=True
        ).stdout.strip()
        if out == "":
            return ""
        time.sleep(0.1)
    return out

from openenv_env import RealityWalkEnvironment, WalkAction  # noqa: E402
from tests.paths import (  # noqa: E402
    CORRECT_ANSWERS,
    CORRECT_PATH,
    WALK_SERVER_JS,
    WRONG_ANSWERS,
)

_FAILURES = []


def check(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(label)


def _new_env():
    assert WALK_SERVER_JS.exists(), f"walk server not found: {WALK_SERVER_JS}"
    return RealityWalkEnvironment(command="node", args=[str(WALK_SERVER_JS)])


def test_correct_path_earns_full_reward():
    env = _new_env()
    try:
        obs = env.reset()
        check("reset() arrives at the seawall", obs.place == "the seawall", obs.place)
        check("reset() states the goal + field questions",
              "walk and learn" in obs.text.lower() and "q1" in obs.text)
        check("reset() is not done, reward 0", not obs.done and obs.reward == 0.0)

        for cmd in CORRECT_PATH:
            obs = env.step(WalkAction(command=cmd))
            assert not obs.done, f"episode ended early on: {cmd}"

        for qid, text in CORRECT_ANSWERS.items():
            obs = env.step(WalkAction(command=f"answer {qid} {text}"))

        check("answering all questions correctly finishes the episode", obs.done)
        check("correct path earns full reward (1.0)", obs.reward == 1.0, str(obs.reward))
        report = obs.report or {}
        check("answer_score is perfect", report.get("answer_score") == 1.0,
              str(report.get("answer_score")))
        check("exploration coverage is complete", report.get("exploration") == 1.0,
              str(report.get("exploration")))
        check("report cites source files",
              all("CANON.md" in q["citation"] for q in report.get("per_question", [])))
        check("state.step_count advanced", env.state.step_count >= len(CORRECT_PATH))
    finally:
        env.close()


def test_wrong_and_empty_answers_earn_low_reward():
    env = _new_env()
    try:
        env.reset()
        obs = None
        for qid, text in WRONG_ANSWERS.items():
            obs = env.step(WalkAction(command=f"answer {qid} {text}"))
        check("wrong answers still finish the episode", obs.done)
        report = obs.report or {}
        check("wrong answers score zero on correctness",
              report.get("answer_score") == 0.0, str(report.get("answer_score")))
        check("wrong/no-walk run earns low reward (< 0.1)", obs.reward < 0.1,
              str(obs.reward))
        check("verifier explains what was missed (per-question)",
              all(q["missed"] for q in report.get("per_question", [])))
    finally:
        env.close()


def test_no_orphan_subprocess():
    env = _new_env()
    env.reset()
    env.step(WalkAction(command="go the north harbor"))
    env.close()
    out = _walk_procs()
    check("no orphaned walk subprocess after close()", out == "",
          out or "none")


if __name__ == "__main__":
    test_correct_path_earns_full_reward()
    test_wrong_and_empty_answers_earn_low_reward()
    test_no_orphan_subprocess()
    if _FAILURES:
        print(f"\n{len(_FAILURES)} check(s) failed: {_FAILURES}")
        sys.exit(1)
    print("\nAll OpenEnv checks passed.")
