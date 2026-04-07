from typing import Any

from src.manual import Manual

from .variables import KeypadSymbol, KeypadVariables


class KeypadManual(Manual):
    """Expert-facing keypad manual with glyph matching rules."""

    def __init__(self, cfg: KeypadVariables):
        super().__init__("Keypad")
        self.cfg = cfg

    @staticmethod
    def recommend_press_positions(
        displayed_symbols: list[KeypadSymbol],
        columns: list[list[KeypadSymbol]],
        serial_last_digit: int,
        battery_count: int,
        has_sig_indicator: bool,
    ) -> list[int]:
        """Return the 1-based press order for the current keypad symbols."""
        displayed_set = set(displayed_symbols)
        matching_columns = [
            column for column in columns if displayed_set.issubset(set(column))
        ]
        if len(matching_columns) != 1:
            raise ValueError("Keypad symbols must match exactly one manual column.")

        base_column = matching_columns[0]
        ordered_symbols = [symbol for symbol in base_column if symbol in displayed_set]

        position_by_symbol = {
            symbol: idx for idx, symbol in enumerate(displayed_symbols, start=1)
        }
        press_order = [position_by_symbol[symbol] for symbol in ordered_symbols]

        # Asymmetric hooks that force additional Driver observations.
        if has_sig_indicator:
            press_order = list(reversed(press_order))
        if battery_count >= 3:
            press_order[1], press_order[2] = press_order[2], press_order[1]

        return press_order

    def content(self) -> str:
        column_lines = "\n".join(
            f"{idx}) {', '.join(repr(symbol) for symbol in column)}"
            for idx, column in enumerate(self.cfg.columns, start=1)
        )

        return """
Keypad Manual (asymmetric variant inspired by glyph-matching keypads)

Data the Expert may request from the Driver:
- The four symbols on the keypad with their button positions (1 to 4).
- Battery count.
- Whether the SIG indicator is lit.

Base glyph rule:
1. Find the single list below that contains all four displayed symbols.
2. Order the displayed symbols according to their order in that list, from left to right.
3. Check if any override rules apply, and if so apply them in the order listed below.
4. Press the buttons in the resulting order, from left to right.

Lists:
""".strip() + f"\n{column_lines}\n\n" + """

Asymmetric override rules (apply in this order):
- If SIG is lit: reverse the resulting order.
- If batteries >= 3: swap the second and third presses.
""".strip()

    def execute_expert_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if name != "python_interpreter":
            return f"Unknown or disallowed expert tool: {name}"
        return self.execute_python_interpreter(arguments)