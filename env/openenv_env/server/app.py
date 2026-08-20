# SPDX-License-Identifier: MIT
"""FastAPI app exposing RealityWalkEnvironment over HTTP/WebSocket (for the HF hub).

Run locally:
    uvicorn openenv_env.server.app:app --host 0.0.0.0 --port 8000
    # or:  python -m openenv_env.server.app

This is only needed to *deploy* the environment (e.g. push to a HuggingFace
Space). The environment itself is a plain object and can be driven in-process —
which is what the tests do — so no HTTP server is required to run an episode.
"""

from __future__ import annotations

import os

from openenv.core.env_server.http_server import create_app

try:
    from ..models import WalkAction, WalkObservation
    from .walk_environment import RealityWalkEnvironment
except ImportError:  # standalone
    from models import WalkAction, WalkObservation  # type: ignore
    from server.walk_environment import RealityWalkEnvironment  # type: ignore

app = create_app(
    RealityWalkEnvironment,
    WalkAction,
    WalkObservation,
    env_name="reality_next_door_walk",
    max_concurrent_envs=int(os.getenv("MAX_CONCURRENT_ENVS", "1")),
)


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main(port=int(os.getenv("PORT", "8000")))
