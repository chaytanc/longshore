# SPDX-License-Identifier: MIT
"""WalkEnv — OpenEnv HTTP client for a deployed RealityWalkEnvironment.

Only needed when talking to a *remote* (HTTP/WebSocket) deployment, e.g. a
HuggingFace Space:

    with WalkEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        print(result.observation.text)
        result = env.step(WalkAction(command="go the north harbor"))

For in-process use (and the tests), construct RealityWalkEnvironment directly and
call reset()/step()/close() — no client needed.
"""

from __future__ import annotations

from typing import Any, Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import WalkAction, WalkObservation


class WalkEnv(EnvClient[WalkAction, WalkObservation, State]):
    """HTTP/WebSocket client mirroring RealityWalkEnvironment's typed I/O."""

    def _step_payload(self, action: WalkAction) -> Dict[str, Any]:
        return {"command": action.command}

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[WalkObservation]:
        obs_data = payload.get("observation", {})
        observation = WalkObservation(
            text=obs_data.get("text", ""),
            place=obs_data.get("place"),
            answered=obs_data.get("answered", []),
            questions_remaining=obs_data.get("questions_remaining", []),
            report=obs_data.get("report"),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
