from dataclasses import dataclass
from random import Random
from typing import Optional

from src.cipher import SYMBOLS

KeypadSymbol = str

_COLUMN_COUNT = 6
_COLUMN_SIZE = 7


def _symbol_universe() -> list[KeypadSymbol]:
    # Keep symbols deterministic and transcribable by removing duplicates/whitespace.
    return [symbol for symbol in dict.fromkeys(SYMBOLS) if symbol and not symbol.isspace()]


def _build_random_columns(rng: Random) -> list[list[KeypadSymbol]]:
    columns: list[list[KeypadSymbol]] = []
    universe = _symbol_universe()
    for _ in range(_COLUMN_COUNT):
        columns.append(rng.sample(universe, _COLUMN_SIZE))
    return columns


def _matching_columns(symbols: list[KeypadSymbol], columns: list[list[KeypadSymbol]]) -> list[int]:
    symbol_set = set(symbols)
    return [
        idx
        for idx, column in enumerate(columns)
        if symbol_set.issubset(set(column))
    ]


@dataclass
class KeypadVariables:
    """Configuration values for one keypad puzzle instance."""

    columns: list[list[KeypadSymbol]]
    displayed_symbols: list[KeypadSymbol]
    serial_last_digit: int
    battery_count: int
    has_sig_indicator: bool

    @staticmethod
    def random(seed: Optional[int] = None) -> "KeypadVariables":
        """Generate a deterministic random keypad scenario."""
        rng = Random(seed)

        # Ensure the chosen four symbols map to exactly one generated column.
        while True:
            columns = _build_random_columns(rng)
            column = rng.choice(columns)
            displayed_symbols = rng.sample(list(column), 4)
            if len(_matching_columns(displayed_symbols, columns)) == 1:
                break

        rng.shuffle(displayed_symbols)

        return KeypadVariables(
            columns=columns,
            displayed_symbols=displayed_symbols,
            serial_last_digit=rng.randint(0, 9),
            battery_count=rng.randint(0, 4),
            has_sig_indicator=rng.choice([True, False]),
        )