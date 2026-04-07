from __future__ import annotations

import random
from typing import Callable

from src.cannon.environment import CannonEnvironment
from src.cannon.manual import CannonManual
from src.cannon.variables import CannonVariables
from src.environment import Environment
from src.manual import Manual
from src.wires.environment import WiresEnvironment
from src.wires.manual import WiresManual
from src.wires.variables import WiresVariables

from .types import PuzzleName

PuzzleBuilder = Callable[[int | None], tuple[Environment, Manual]]


def build_wires(seed: int | None) -> tuple[Environment, Manual]:
    cfg = WiresVariables.random(seed=seed)
    return WiresEnvironment(cfg), WiresManual(cfg)


def build_cannon(seed: int | None) -> tuple[Environment, Manual]:
    rng = random.Random(seed)

    # Keep sampling until we get a solvable instance under integer angle search.
    for _ in range(1000):
        candidate_seed = rng.randint(0, 10_000_000)
        cfg = CannonVariables.random(seed=candidate_seed)
        env = CannonEnvironment(cfg)
        if env.is_solvable():
            return env, CannonManual(cfg)

    raise RuntimeError("Could not generate a solvable cannon instance.")


PUZZLE_BUILDERS: dict[PuzzleName, PuzzleBuilder] = {
    "wires": build_wires,
    "cannon": build_cannon,
}


def available_puzzles() -> list[PuzzleName]:
    return list(PUZZLE_BUILDERS.keys())


def build_puzzle(puzzle: PuzzleName, seed: int | None) -> tuple[Environment, Manual]:
    return PUZZLE_BUILDERS[puzzle](seed)
