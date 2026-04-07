from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.manual import Manual

if TYPE_CHECKING:
    from .variables import WhofirstVariables


class WhofirstManual(Manual):
    """Expert-facing Who's on First rulebook."""

    def __init__(self, cfg: WhofirstVariables):
        super().__init__("Whofirst")
        self.cfg = cfg

    def recommend_press_position(self, display: str, labels: list[str]) -> int:
        """Return the 1-based button position to press for one round."""
        if len(labels) != 6:
            raise ValueError("Who's on First expects exactly 6 labels.")

        normalized_display = display.strip().upper()
        if normalized_display not in self.cfg.display_position:
            raise ValueError(f"Unknown display word: {display!r}")

        read_position = self.cfg.display_position[normalized_display]
        read_word = labels[read_position - 1].strip().upper()
        if read_word not in self.cfg.label_priority:
            raise ValueError(f"Unknown label word: {read_word!r}")

        priority = self.cfg.label_priority[read_word]
        normalized_labels = [label.strip().upper() for label in labels]
        for candidate in priority:
            if candidate in normalized_labels:
                return normalized_labels.index(candidate) + 1

        raise ValueError("No priority match found for current labels.")

    def expert_tool_instructions(self) -> str:
        return (
            "Available Expert tools: python_interpreter(code). "
            "Use it to automate table lookup when helpful, but first ask the Driver for exact display text "
            "and all six labels with positions 1..6."
        )

    def content(self) -> str:
        display_lines = "\n".join(
            f"- {word!r}: read position {position}"
            for word, position in self.cfg.display_position.items()
        )
        label_lines = "\n".join(
            f"- {word}: {', '.join(priority)}"
            for word, priority in self.cfg.label_priority.items()
        )

        return (
            "Who's on First Manual\n\n"
            "Role and objective:\n"
            "- You are the Expert. You cannot inspect the module directly.\n"
            "- The Driver can inspect and press buttons.\n"
            "- Goal: solve every round by returning one explicit 1-based button position each round.\n\n"
            "Require from the Driver the display word and all six button labels with positions 1..6.\n"
            "Round-solving algorithm:\n"
            "1. Normalize all words to uppercase for lookup only.\n"
            "2. Use the display table to find the read position (1..6).\n"
            "3. Read the label currently at that position.\n"
            "4. Using the label you read, look up its priority list.\n"
            "5. Scan the priority list top-down; choose the first word present among current six labels.\n"
            "Recommended communication pattern:\n"
            "- If data is complete: reply with one unambiguous position.\n"
            "- Avoid giving multiple candidate positions.\n\n"
            "Display to read-position table:\n"
            f"{display_lines}\n\n"
            "Label priority lists:\n"
            f"{label_lines}"
        )

    def execute_expert_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if name != "python_interpreter":
            return f"Unknown or disallowed expert tool: {name}"
        return self.execute_python_interpreter(arguments)