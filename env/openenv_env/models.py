# SPDX-License-Identifier: MIT
"""Typed Action/Observation for the Reality-Next-Door walk-and-learn OpenEnv env.

These subclass OpenEnv's pydantic ``Action``/``Observation`` base classes, so the
HTTP server and client serialize them for free.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class WalkAction(Action):
    """One free-text command per step.

    Grammar (see ``reality_walk.task.parse_action``):
        look | map | where | join
        go <place> | talk_to <person> | do <action> | work <shift>
        answer <qid> <text> | submit
    """

    command: str = Field(
        ...,
        description=(
            "A single command, e.g. 'go the north harbor', 'talk_to Hale', "
            "'do sit a deep hour', 'answer q1 it is a deep hour ...', 'submit'."
        ),
    )


class WalkObservation(Observation):
    """What the agent sees after a step: the world's own text, plus task state."""

    text: str = Field(default="", description="The MCP tool output or task feedback.")
    place: Optional[str] = Field(default=None, description="Where the agent stands.")
    answered: List[str] = Field(
        default_factory=list, description="Question ids answered so far."
    )
    questions_remaining: List[str] = Field(
        default_factory=list, description="Question ids still open."
    )
    report: Optional[Dict[str, Any]] = Field(
        default=None, description="The full grading report (only present when done)."
    )
