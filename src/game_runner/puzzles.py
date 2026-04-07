from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from src.cannon import DRIVER_ACTION_EXAMPLE_ARGS_JSON as CANNON_DRIVER_ACTION_EXAMPLE_ARGS_JSON
from src.cannon import DRIVER_ACTION_NAME as CANNON_DRIVER_ACTION_NAME
from src.cannon.environment import CannonEnvironment
from src.cannon.manual import CannonManual
from src.cannon.variables import CannonVariables
from src.environment import Environment
from src.keypad import DRIVER_ACTION_EXAMPLE_ARGS_JSON as KEYPAD_DRIVER_ACTION_EXAMPLE_ARGS_JSON
from src.keypad import DRIVER_ACTION_NAME as KEYPAD_DRIVER_ACTION_NAME
from src.keypad.environment import KeypadEnvironment
from src.keypad.manual import KeypadManual
from src.keypad.variables import KeypadVariables
from src.manual import Manual
from src.wires import DRIVER_ACTION_EXAMPLE_ARGS_JSON as WIRES_DRIVER_ACTION_EXAMPLE_ARGS_JSON
from src.wires import DRIVER_ACTION_NAME as WIRES_DRIVER_ACTION_NAME
from src.wires.environment import WiresEnvironment
from src.wires.manual import WiresManual
from src.wires.variables import WiresVariables
from src.whofirst import DRIVER_ACTION_EXAMPLE_ARGS_JSON as WHOFIRST_DRIVER_ACTION_EXAMPLE_ARGS_JSON
from src.whofirst import DRIVER_ACTION_NAME as WHOFIRST_DRIVER_ACTION_NAME
from src.whofirst.environment import WhofirstEnvironment
from src.whofirst.manual import WhofirstManual
from src.whofirst.variables import WhofirstVariables

from .types import PuzzleName

PuzzleBuilder = Callable[[int | None], tuple[Environment, Manual]]


@dataclass(frozen=True)
class PuzzleSpec:
    builder: PuzzleBuilder
    driver_action_name: str
    driver_action_example_args_json: str


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


def build_keypad(seed: int | None) -> tuple[Environment, Manual]:
    cfg = KeypadVariables.random(seed=seed)
    return KeypadEnvironment(cfg), KeypadManual(cfg)


def build_whofirst(seed: int | None) -> tuple[Environment, Manual]:
    cfg = WhofirstVariables.random(seed=seed)
    return WhofirstEnvironment(cfg), WhofirstManual(cfg)


PUZZLE_SPECS: dict[PuzzleName, PuzzleSpec] = {
    "wires": PuzzleSpec(
        builder=build_wires,
        driver_action_name=WIRES_DRIVER_ACTION_NAME,
        driver_action_example_args_json=WIRES_DRIVER_ACTION_EXAMPLE_ARGS_JSON,
    ),
    "cannon": PuzzleSpec(
        builder=build_cannon,
        driver_action_name=CANNON_DRIVER_ACTION_NAME,
        driver_action_example_args_json=CANNON_DRIVER_ACTION_EXAMPLE_ARGS_JSON,
    ),
    "keypad": PuzzleSpec(
        builder=build_keypad,
        driver_action_name=KEYPAD_DRIVER_ACTION_NAME,
        driver_action_example_args_json=KEYPAD_DRIVER_ACTION_EXAMPLE_ARGS_JSON,
    ),
    "whofirst": PuzzleSpec(
        builder=build_whofirst,
        driver_action_name=WHOFIRST_DRIVER_ACTION_NAME,
        driver_action_example_args_json=WHOFIRST_DRIVER_ACTION_EXAMPLE_ARGS_JSON,
    ),
}


def available_puzzles() -> list[PuzzleName]:
    return list(PUZZLE_SPECS.keys())


def build_puzzle(puzzle: PuzzleName, seed: int | None) -> tuple[Environment, Manual]:
    return PUZZLE_SPECS[puzzle].builder(seed)


def driver_action_prompt_fields(puzzle: PuzzleName) -> tuple[str, str]:
    spec = PUZZLE_SPECS[puzzle]
    return spec.driver_action_name, spec.driver_action_example_args_json
