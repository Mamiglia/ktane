from typing import Any

from src.manual import Manual

from .variables import WireColor, WiresVariables


class WiresManual(Manual):
    """Expert-facing rulebook for deciding which wire index to cut."""

    def __init__(self, cfg: WiresVariables):
        super().__init__("Wires")
        self.cfg = cfg

    @staticmethod
    def recommend_cut_position(
        wire_colors: list[WireColor],
        serial_last_digit: int,
        battery_count: int,
        has_lit_car_indicator: bool,
        has_parallel_port: bool,
    ) -> int:
        """Return the 1-based wire position to cut."""
        count = len(wire_colors)

        if count not in {3, 4, 5, 6}:
            raise ValueError("Wires module expects 3 to 6 wires.")

        serial_is_odd = (serial_last_digit % 2) == 1

        # Asymmetric variant hooks: these values are inspectable by Driver,
        # but not available to the Expert unless shared explicitly.
        if count in {5, 6} and has_lit_car_indicator and battery_count >= 3:
            black_positions = [
                idx for idx, color in enumerate(wire_colors, start=1) if color == "black"
            ]
            if black_positions:
                return black_positions[-1]

        if count == 6 and has_parallel_port and wire_colors.count("blue") >= 2:
            return 2

        if count == 3:
            if "red" not in wire_colors:
                return 2
            if wire_colors[-1] == "white":
                return 3
            if wire_colors.count("blue") > 1:
                return max(
                    idx
                    for idx, color in enumerate(wire_colors, start=1)
                    if color == "blue"
                )
            return 3

        if count == 4:
            if wire_colors.count("red") > 1 and serial_is_odd:
                return max(
                    idx
                    for idx, color in enumerate(wire_colors, start=1)
                    if color == "red"
                )
            if wire_colors[-1] == "yellow" and "red" not in wire_colors:
                return 1
            if wire_colors.count("blue") == 1:
                return 1
            if wire_colors.count("yellow") > 1:
                return 4
            return 2

        if count == 5:
            if wire_colors[-1] == "black" and serial_is_odd:
                return 4
            if wire_colors.count("red") == 1 and wire_colors.count("yellow") > 1:
                return 1
            if "black" not in wire_colors:
                return 2
            return 1

        # count == 6
        if "yellow" not in wire_colors and serial_is_odd:
            return 3
        if wire_colors.count("yellow") == 1 and wire_colors.count("white") > 1:
            return 4
        if "red" not in wire_colors:
            return 6
        return 4

    def content(self) -> str:
        return """
Wires Manual (asymmetric variant inspired by 'On the Subject of Wires')

Data the Expert must ask from the Driver:
- Ordered wire colors from top to bottom.
- Last serial digit.
- Battery count.
- Whether the CAR indicator is lit.
- Whether a parallel port is present.

Priority override rules:
1. If there are 5 or 6 wires, CAR is lit, and batteries >= 3: cut the last black wire.
2. If there are 6 wires, a parallel port is present, and at least 2 wires are blue: cut wire 2.

Base rules for 3 wires:
- If there are no red wires: cut wire 2.
- Otherwise, if the last wire is white: cut wire 3.
- Otherwise, if there is more than one blue wire: cut the last blue wire.
- Otherwise: cut wire 3.

Base rules for 4 wires:
- If there is more than one red wire and the serial last digit is odd: cut the last red wire.
- Otherwise, if the last wire is yellow and there are no red wires: cut wire 1.
- Otherwise, if there is exactly one blue wire: cut wire 1.
- Otherwise, if there is more than one yellow wire: cut wire 4.
- Otherwise: cut wire 2.

Base rules for 5 wires:
- If the last wire is black and serial last digit is odd: cut wire 4.
- Otherwise, if there is exactly one red wire and more than one yellow wire: cut wire 1.
- Otherwise, if there are no black wires: cut wire 2.
- Otherwise: cut wire 1.

Base rules for 6 wires:
- If there are no yellow wires and the serial last digit is odd: cut wire 3.
- Otherwise, if there is exactly one yellow wire and more than one white wire: cut wire 4.
- Otherwise, if there are no red wires: cut wire 6.
- Otherwise: cut wire 4.
""".strip()

    def execute_expert_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if name != "python_interpreter":
            return f"Unknown or disallowed expert tool: {name}"
        return self.execute_python_interpreter(arguments)
