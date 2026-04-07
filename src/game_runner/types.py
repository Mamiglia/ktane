from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Role = Literal["driver", "expert"]
PuzzleName = Literal["wires", "cannon"]

DEFAULT_MAX_TURNS = 10


@dataclass
class RunResult:
    puzzle: PuzzleName
    solved: bool
    reason: str
    turns: int
    transcript: list[dict[str, Any]]
    driver_system_prompt: str
    expert_system_prompt: str
    driver_messages: list[dict[str, str]]
    expert_messages: list[dict[str, str]]
