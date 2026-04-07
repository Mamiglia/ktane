from dataclasses import dataclass, field
from random import Random
from typing import Optional

from .rules import DISPLAY_POSITION, LABEL_PRIORITY


DisplayWord = str
LabelWord = str


@dataclass(frozen=True)
class WhofirstRound:
    """Static configuration for one Who's on First round."""

    display: DisplayWord
    labels: list[LabelWord]


@dataclass
class WhofirstVariables:
    """Configuration values for one Who's on First puzzle instance."""

    rounds: list[WhofirstRound]
    display_position: dict[str, int] = field(repr=False)
    label_priority: dict[str, list[str]] = field(repr=False)

    @staticmethod
    def random(seed: Optional[int] = None) -> "WhofirstVariables":
        """Generate deterministic rounds and randomized rule tables."""
        rng = Random(seed)
        display_words = list(DISPLAY_POSITION.keys())
        label_words = list(LABEL_PRIORITY.keys())

        display_position = {
            word: rng.randint(1, 6)
            for word in display_words
        }
        label_priority = {
            word: rng.sample(label_words, len(label_words))
            for word in label_words
        }

        rounds: list[WhofirstRound] = []
        for _ in range(rng.randint(1, 5)):
            display = rng.choice(display_words)
            labels = rng.sample(label_words, 6)
            rounds.append(WhofirstRound(display=display, labels=labels))

        return WhofirstVariables(
            rounds=rounds,
            display_position=display_position,
            label_priority=label_priority,
        )