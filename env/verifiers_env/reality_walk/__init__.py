# SPDX-License-Identifier: MIT
"""Prime Intellect **Verifiers** environment for the walk-and-learn task (secondary).

`load_environment(**kwargs)` is the Environments-Hub entry point convention: it
returns a `verifiers.Environment`. Here it returns a `MultiTurnEnv` because the
task is inherently multi-turn — the policy has to *walk* the world (many MCP tool
calls) before it can answer. The environment reuses the exact same building
blocks as the OpenEnv adapter:

    * reality_walk.bridge.MCPWalkBridge  — launches the published walk MCP server
    * reality_walk.task.WalkEpisode      — the episode engine (world calls + answers)
    * reality_walk.task.grade_answers    — the canon grader, wrapped as a vf.Rubric

Mapping onto Verifiers 0.3.0 (verified against the installed package):
    setup_state(state)        -> launch the walk subprocess, look() at the seawall,
                                 append that text to the prompt.
    env_response(msgs, state) -> parse the assistant's command, step the episode,
                                 return the world text; on done, set
                                 state["final_env_response"] to stop the rollout.
    a vf.Rubric reward func    -> grade_answers over the recorded answers/exploration.
    @vf.cleanup handler        -> close the MCP subprocess (no orphans).

HONEST GAP: a *full* RL/eval rollout drives an LLM policy through an
OpenAI-compatible `Client`, which needs a model endpoint + credentials, so it
can't run in offline CI. The world bridge, the env wiring, and the rubric are
all exercised offline by tests/test_verifiers_env.py (which drives env_response
with scripted commands and scores the resulting state). To run a real rollout:
`vf-eval reality-walk -m <model>` or `prime env eval` against a served model.
"""

from __future__ import annotations

import os
import shlex
from typing import Any, List, Optional

import verifiers as vf
from datasets import Dataset
from verifiers.utils.message_utils import concat_messages

from reality_walk.bridge import DEFAULT_ARGS, DEFAULT_COMMAND, MCPWalkBridge
from reality_walk.task import (
    DEFAULT_STEP_BUDGET,
    FIELD_QUESTIONS,
    WalkEpisode,
    grade_answers,
)

SYSTEM_PROMPT = (
    "You are an agent exploring The Reality Next Door, a cited walkable world served "
    "over MCP. Issue exactly one command per turn. Commands: look; map; where; "
    "go <place>; talk_to <person>; do <action>; work <shift>; answer <qid> <text>; "
    "submit. You cannot answer the field questions without walking to the right "
    "places, talking to the right people, and doing the right work first."
)


def _goal_prompt(questions: List[dict], step_budget: int) -> str:
    qs = "\n".join(f"- {q['id']}: {q['prompt']}" for q in questions)
    return (
        "Goal: explore the world, then answer these grounded field questions with "
        "`answer <qid> <text>` and `submit`.\n\n"
        f"{qs}\n\nStep budget: {step_budget}. Your arrival follows."
    )


class RealityWalkVerifiersEnv(vf.MultiTurnEnv):
    """A Verifiers MultiTurnEnv over the published walk MCP server."""

    def __init__(
        self,
        bridge_factory,
        questions: List[dict] = FIELD_QUESTIONS,
        step_budget: int = DEFAULT_STEP_BUDGET,
        **kwargs: Any,
    ) -> None:
        # max_turns generous vs. the episode's own budget; both terminate cleanly.
        super().__init__(max_turns=step_budget + 10, **kwargs)
        self._factory = bridge_factory
        self._questions = questions
        self._budget = step_budget

    async def setup_state(self, state: vf.State) -> vf.State:
        episode = WalkEpisode(
            self._factory, questions=self._questions, step_budget=self._budget
        )
        outcome = episode.reset()
        state["_episode"] = episode
        state["answers"] = {}
        state["engaged"] = []
        # Let the agent see the seawall: append the arrival to the prompt.
        state["prompt"] = concat_messages(
            [state["prompt"], [{"role": "user", "content": outcome.text}]]
        )
        return state

    async def env_response(
        self, messages: vf.Messages, state: vf.State, **kwargs: Any
    ) -> vf.Messages:
        command = self._last_command(messages)
        episode: WalkEpisode = state["_episode"]
        outcome = episode.step(command)
        state["answers"] = dict(episode.answers)
        state["engaged"] = sorted(episode.engaged)
        reply = [{"role": "user", "content": outcome.text}]
        if outcome.done:
            state["report"] = episode.final_report
            state["final_env_response"] = reply
        return reply

    @vf.cleanup
    async def _close_episode(self, state: vf.State, **kwargs: Any) -> None:
        episode = state.get("_episode")
        if episode is not None:
            episode.close()

    @staticmethod
    def _last_command(messages: vf.Messages) -> str:
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content", "")
                return content if isinstance(content, str) else str(content)
        # Fallback: last message content.
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", ""))
        return ""


def build_rubric(questions: List[dict] = FIELD_QUESTIONS) -> vf.Rubric:
    """A genuine vf.Rubric: the reward IS grade_answers over the walked episode."""

    async def field_question_reward(state, **kwargs) -> float:
        report = grade_answers(
            state.get("answers", {}), questions, set(state.get("engaged", []))
        )
        # Cache the full report so eval output can explain right/missed + citations.
        state["report"] = report
        return report["reward"]

    async def answer_correctness(state, **kwargs) -> float:
        return grade_answers(
            state.get("answers", {}), questions, set(state.get("engaged", []))
        )["answer_score"]

    async def exploration_coverage(state, **kwargs) -> float:
        return grade_answers(
            state.get("answers", {}), questions, set(state.get("engaged", []))
        )["exploration"]

    # Weighted reward = field_question_reward; the other two are 0-weight metrics.
    return vf.Rubric(
        funcs=[field_question_reward, answer_correctness, exploration_coverage],
        weights=[1.0, 0.0, 0.0],
    )


def load_environment(
    walk_server_js: Optional[str] = None,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    step_budget: int = DEFAULT_STEP_BUDGET,
    **kwargs: Any,
) -> vf.Environment:
    """Environments-Hub entry point.

    Args:
        walk_server_js: path to a local ``walk/server.js`` for an offline run.
        command/args: explicit launch command (defaults to
            ``npx -y reality-next-door-walk`` if nothing else is given).
        cwd: working directory for the subprocess.
        step_budget: field-question step budget.
    """
    walk_server_js = walk_server_js or os.getenv("WALK_SERVER_JS")
    if command is None and walk_server_js:
        command, args = "node", [walk_server_js]
    if command is None:
        command = os.getenv("WALK_SERVER_COMMAND", DEFAULT_COMMAND)
        env_args = os.getenv("WALK_SERVER_ARGS")
        args = shlex.split(env_args) if env_args else list(DEFAULT_ARGS)

    def bridge_factory() -> MCPWalkBridge:
        return MCPWalkBridge(command=command, args=args, cwd=cwd).start()

    # One-row dataset: the goal + questions. The live seawall arrival is appended
    # per-rollout in setup_state (it depends on a running subprocess).
    dataset = Dataset.from_list(
        [
            {
                "question": _goal_prompt(FIELD_QUESTIONS, step_budget),
                "answer": "",
                "info": {"task": "reality-walk"},
            }
        ]
    )

    return RealityWalkVerifiersEnv(
        bridge_factory=bridge_factory,
        step_budget=step_budget,
        dataset=dataset,
        system_prompt=SYSTEM_PROMPT,
        rubric=build_rubric(FIELD_QUESTIONS),
        **kwargs,
    )
