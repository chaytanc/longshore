# SPDX-License-Identifier: MIT
"""RealityWalkEnvironment — the OpenEnv-compatible environment (primary adapter).

This is a thin OpenEnv ``Environment`` over the shared task engine
(`reality_walk.task.WalkEpisode`), which in turn drives the published walk MCP
server through `reality_walk.bridge.MCPWalkBridge`. reset()/step()/close() map
straight onto the OpenEnv Gym-style API:

    reset()        -> launch the walk server subprocess, look() at the seawall,
                      and state the goal + field questions.
    step(action)   -> parse the command, call the matching MCP tool (or record an
                      answer / submit), and return the new observation. Reward is
                      0 on intermediate steps and the blended task reward at done.
    close()        -> tear down the MCP subprocess (no orphans).

The world is never reimplemented here: every place, person, and mechanic comes
from the one npm package. Configure the launch with constructor args or env vars:

    WALK_SERVER_JS       absolute path to a local walk/server.js  (offline; tests)
    WALK_SERVER_COMMAND  executable (default: npx)
    WALK_SERVER_ARGS     space-joined args (default: -y reality-next-door-walk)
    WALK_STEP_BUDGET     integer step budget (default: 40)
"""

from __future__ import annotations

import os
import shlex
from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:  # in-package import
    from ..models import WalkAction, WalkObservation
except ImportError:  # standalone (server/ on the path)
    from models import WalkAction, WalkObservation  # type: ignore

from reality_walk.bridge import DEFAULT_ARGS, DEFAULT_COMMAND, MCPWalkBridge
from reality_walk.task import DEFAULT_STEP_BUDGET, StepOutcome, WalkEpisode


class RealityWalkEnvironment(Environment):
    """OpenEnv environment: a walk-and-learn episode over the cited walkable world."""

    # One walk MCP subprocess per episode; do not share across sessions.
    SUPPORTS_CONCURRENT_SESSIONS = False

    def __init__(
        self,
        command: Optional[str] = None,
        args: Optional[list] = None,
        cwd: Optional[str] = None,
        step_budget: Optional[int] = None,
    ) -> None:
        super().__init__()
        server_js = os.getenv("WALK_SERVER_JS")
        if command is None and server_js:
            command, args = "node", [server_js]
        if command is None:
            command = os.getenv("WALK_SERVER_COMMAND", DEFAULT_COMMAND)
            env_args = os.getenv("WALK_SERVER_ARGS")
            args = shlex.split(env_args) if env_args else list(DEFAULT_ARGS)
        self._command, self._args, self._cwd = command, args, cwd
        self._budget = int(
            step_budget
            if step_budget is not None
            else os.getenv("WALK_STEP_BUDGET", DEFAULT_STEP_BUDGET)
        )

        self._episode = WalkEpisode(self._make_bridge, step_budget=self._budget)
        self._state = State(episode_id=str(uuid4()), step_count=0)

    def _make_bridge(self) -> MCPWalkBridge:
        return MCPWalkBridge(
            command=self._command, args=self._args, cwd=self._cwd
        ).start()

    # -- OpenEnv API ----------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> WalkObservation:
        outcome = self._episode.reset()
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        return self._to_obs(outcome)

    def step(
        self,
        action: WalkAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> WalkObservation:
        self._state.step_count += 1
        outcome = self._episode.step(action.command)
        return self._to_obs(outcome)

    @property
    def state(self) -> State:
        return self._state

    def close(self) -> None:
        self._episode.close()

    # -- helpers --------------------------------------------------------------

    def _to_obs(self, outcome: StepOutcome) -> WalkObservation:
        meta = outcome.metadata
        return WalkObservation(
            text=outcome.text,
            done=outcome.done,
            reward=outcome.reward,
            place=meta.get("place"),
            answered=meta.get("answered", []),
            questions_remaining=meta.get("questions_remaining", []),
            report=meta.get("report"),
            metadata={
                "steps": meta.get("steps"),
                "num_questions": meta.get("num_questions"),
            },
        )
