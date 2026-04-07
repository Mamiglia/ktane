from typing import Any

from src.environment import Environment

from .manual import WhofirstManual
from .variables import WhofirstVariables


class WhofirstEnvironment(Environment):
    """Driver-facing Who's on First module with staged rounds."""

    def __init__(self, cfg: WhofirstVariables):
        super().__init__(
            name="Who's on First Environment",
            description=(
                "You are the Driver for a Who's on First module with one display and six labeled buttons. "
                "The module has multiple rounds and must be solved in order. "
                "Only the Expert knows the rules and knows the solution for each round. Ask them before pressing any buttons! "
                "When reporting observations, include both the display word and the six labels with positions 1..6. "
                "Spelling and punctuation matter."
            ),
            places=["display", "button panel", "progress"],
        )
        self.cfg = cfg
        self.current_round = 0
        self.last_press: int | None = None

        self._refresh_places()

    def _refresh_places(self) -> None:
        if self.current_round >= len(self.cfg.rounds):
            self.places_info["display"] = "The module display is dark."
            self.places_info["button panel"] = "All six buttons are inactive."
            self.places_info["progress"] = "All rounds solved."
            return

        round_cfg = self.cfg.rounds[self.current_round]
        button_lines = [
            f"{index}. {label!r}"
            for index, label in enumerate(round_cfg.labels, start=1)
        ]
        self.places_info["display"] = f"Display reads: {round_cfg.display!r}."
        self.places_info["button panel"] = (
            f"Display reads: {round_cfg.display!r}.\n"
            + "Current labels:\n"
            + "\n".join(button_lines)
        )
        self.places_info["progress"] = (
            f"Round {self.current_round + 1} of {len(self.cfg.rounds)}. "
            "Workflow: inspect display + button panel, send exact transcription to Expert, "
            "wait for one 1-based position, then press that position."
        )

    def press_whofirst_button(self, position: int, manual: WhofirstManual) -> tuple[str, bool]:
        """Submit a 1-based button position for the current round."""
        if self.current_round >= len(self.cfg.rounds):
            return "Module already solved.", True

        if position < 1 or position > 6:
            return "press_whofirst_button error: position must be between 1 and 6", False

        self.last_press = position
        round_cfg = self.cfg.rounds[self.current_round]
        expected = manual.recommend_press_position(round_cfg.display, round_cfg.labels)

        if position == expected:
            self.current_round += 1
            self._refresh_places()
            if self.current_round >= len(self.cfg.rounds):
                return f"Pressed button {position}. Correct. Module solved.", True
            return (
                f"Pressed button {position}. Correct. "
                f"Advance to round {self.current_round + 1}."
            ), False

        return (
            f"Pressed button {position}. Incorrect for this round. "
            "No progress made; inspect the current display and labels again."
        ), False

    def execute_driver_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        manual: WhofirstManual,
    ) -> tuple[str, bool, bool]:
        if name == "inspect":
            return super().execute_driver_tool(name, arguments, manual)

        if name != "press_whofirst_button":
            return f"Unknown or disallowed driver tool: {name}", False, False

        try:
            position = int(arguments.get("position", 0))
        except (TypeError, ValueError):
            return "press_whofirst_button error: position must be an integer", False, False

        result, solved = self.press_whofirst_button(position, manual)
        success = "error" not in result
        return result, success, solved

    @property
    def variables(self) -> dict:
        return {
            "rounds": [
                {
                    "display": round_cfg.display,
                    "labels": round_cfg.labels,
                }
                for round_cfg in self.cfg.rounds
            ],
            "current_round": self.current_round,
        }