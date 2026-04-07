from dataclasses import dataclass
from random import Random
from typing import Literal, Optional

WireColor = Literal["red", "blue", "yellow", "white", "black"]


@dataclass
class WiresVariables:
    """Configuration values for one wires puzzle instance."""

    wire_colors: list[WireColor]
    serial_last_digit: int
    battery_count: int
    has_lit_car_indicator: bool
    has_parallel_port: bool

    @property
    def wire_count(self) -> int:
        return len(self.wire_colors)

    @staticmethod
    def random(seed: Optional[int] = None) -> "WiresVariables":
        """Generate a deterministic random puzzle instance."""
        rng = Random(seed)

        wire_count = rng.randint(3, 6)
        palette: list[WireColor] = ["red", "blue", "yellow", "white", "black"]
        wire_colors: list[WireColor] = [rng.choice(palette) for _ in range(wire_count)]

        serial_last_digit = rng.randint(0, 9)
        battery_count = rng.randint(0, 4)
        has_lit_car_indicator = rng.choice([True, False])
        has_parallel_port = rng.choice([True, False])

        return WiresVariables(
            wire_colors=wire_colors,
            serial_last_digit=serial_last_digit,
            battery_count=battery_count,
            has_lit_car_indicator=has_lit_car_indicator,
            has_parallel_port=has_parallel_port,
        )
