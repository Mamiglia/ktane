from typing import Any

from src.environment import Environment
from src.manual import Manual

from .manual import WiresManual
from .variables import WiresVariables


class WiresEnvironment(Environment):
    """Driver-facing wires environment with inspectable observation points only."""

    def __init__(self, cfg: WiresVariables):
        super().__init__(
            name="Wires Environment",
            description=(
                "You are in front of a wire panel with numbered horizontal wires "
                "and a cutter."
            ),
            places=[
                "wire panel",
                "serial plate",
                "battery tray",
                "indicator strip",
                "port panel",
            ],
        )
        self.cfg = cfg

        wire_lines = [
            f"{index}. {color}" for index, color in enumerate(self.cfg.wire_colors, start=1)
        ]
        self.places_info["wire panel"] = "Visible wires:\n" + "\n".join(wire_lines)
        self.places_info["serial plate"] = (
            f"The serial number ends with digit {self.cfg.serial_last_digit}."
        )
        self.places_info["battery tray"] = (
            f"There are {self.cfg.battery_count} batteries installed."
        )
        self.places_info["indicator strip"] = (
            "The CAR indicator is lit."
            if self.cfg.has_lit_car_indicator
            else "The CAR indicator is not lit."
        )
        self.places_info["port panel"] = (
            "A parallel port is present."
            if self.cfg.has_parallel_port
            else "No parallel port is present."
        )
        self.cut_position: int | None = None

    def cut_wire(self, position: int) -> str:
        """Perform the driver action of cutting a 1-based wire position."""
        if position < 1 or position > self.cfg.wire_count:
            return (
                f"Invalid wire position {position}. "
                f"Choose a value between 1 and {self.cfg.wire_count}."
            )

        self.cut_position = position
        color = self.cfg.wire_colors[position - 1]
        return f"You cut wire {position} ({color})."

    def execute_driver_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        manual: Manual,
    ) -> tuple[str, bool, bool]:
        if name == "inspect":
            return super().execute_driver_tool(name, arguments, manual)

        if name != "cut_wire":
            return f"Unknown or disallowed driver tool: {name}", False, False

        if not isinstance(manual, WiresManual):
            return "cut_wire error: invalid puzzle environment/manual pairing", False, False

        try:
            position = int(arguments.get("position", 0))
        except (TypeError, ValueError):
            return "cut_wire error: position must be an integer", False, False

        result = self.cut_wire(position)
        expected = manual.recommend_cut_position(
            self.cfg.wire_colors,
            self.cfg.serial_last_digit,
            self.cfg.battery_count,
            self.cfg.has_lit_car_indicator,
            self.cfg.has_parallel_port,
        )
        return result, True, position == expected

    @property
    def variables(self) -> dict:
        return {
            "wire_colors": self.cfg.wire_colors,
            "serial_last_digit": self.cfg.serial_last_digit,
            "battery_count": self.cfg.battery_count,
            "has_lit_car_indicator": self.cfg.has_lit_car_indicator,
            "has_parallel_port": self.cfg.has_parallel_port,
        }
