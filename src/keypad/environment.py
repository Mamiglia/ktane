from typing import Any

from src.environment import Environment
from src.manual import Manual

from .manual import KeypadManual
from .variables import KeypadVariables


class KeypadEnvironment(Environment):
    """Driver-facing keypad environment with inspect-only observations."""

    def __init__(self, cfg: KeypadVariables):
        super().__init__(
            name="Keypad Environment",
            description=(
                "You are facing a keypad module with four symbol buttons and "
                "a central submit switch."
            ),
            places=["keypad", "serial plate", "battery tray", "indicator strip"],
        )
        self.cfg = cfg

        keypad_lines = [
            f"{idx}. {symbol!r}"
            for idx, symbol in enumerate(self.cfg.displayed_symbols, start=1)
        ]
        self.places_info["keypad"] = "Visible keypad symbols:\n" + "\n".join(keypad_lines)
        self.places_info["serial plate"] = (
            f"The serial number ends with digit {self.cfg.serial_last_digit}."
        )
        self.places_info["battery tray"] = (
            f"There are {self.cfg.battery_count} batteries installed."
        )
        self.places_info["indicator strip"] = (
            "The SIG indicator is lit."
            if self.cfg.has_sig_indicator
            else "The SIG indicator is not lit."
        )

        self.submitted_order: list[int] | None = None

    def press_keypad_order(self, order: list[int]) -> str:
        """Submit a 1-based sequence of button positions."""
        if len(order) != 4:
            return "press_keypad_order error: order must contain exactly 4 positions"
        
        if sorted(order) == [0, 1, 2, 3]:
            order = [pos + 1 for pos in order]  # Allow 0-based indexing as a convenience.

        if sorted(order) != [1, 2, 3, 4]:
            return "press_keypad_order error: order must be a permutation of [1, 2, 3, 4]"

        self.submitted_order = order
        pressed_symbols = [self.cfg.displayed_symbols[pos - 1] for pos in order]
        return (
            f"Submitted keypad order {order}. "
            f"Pressed symbols in sequence: {', '.join(repr(symbol) for symbol in pressed_symbols)}."
        )

    def execute_driver_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        manual: KeypadManual,
    ) -> tuple[str, bool, bool]:
        if name == "inspect":
            return super().execute_driver_tool(name, arguments, manual)

        if name != "press_keypad_order":
            return f"Unknown or disallowed driver tool: {name}", False, False

        raw_order = arguments.get("order")
        if not isinstance(raw_order, list):
            return "press_keypad_order error: order must be a JSON array", False, False

        try:
            order = [int(value) for value in raw_order]
        except (TypeError, ValueError):
            return "press_keypad_order error: order values must be integers", False, False

        result = self.press_keypad_order(order)
        if "error" in result:
            return result, False, False

        expected = manual.recommend_press_positions(
            displayed_symbols=self.cfg.displayed_symbols,
            columns=self.cfg.columns,
            serial_last_digit=self.cfg.serial_last_digit,
            battery_count=self.cfg.battery_count,
            has_sig_indicator=self.cfg.has_sig_indicator,
        )
        return result, True, order == expected

    @property
    def variables(self) -> dict:
        return {
            "columns": self.cfg.columns,
            "displayed_symbols": self.cfg.displayed_symbols,
            "serial_last_digit": self.cfg.serial_last_digit,
            "battery_count": self.cfg.battery_count,
            "has_sig_indicator": self.cfg.has_sig_indicator,
        }