from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class CannonVariables:
    color: Literal["red", "blue", "green", 'yellow', 'purple', 'black'] = 'red'
    height: float = 0
    distance: float = 0
    angle: float = 0
    velocity: float = 0
    mass: float = 0
    
    @staticmethod
    def random(seed: Optional[int] = None) -> 'CannonVariables':
        import random
        if seed is not None:
            random.seed(seed)
        
        color = random.choice(["red", "blue", "green", 'yellow', 'purple', 'black'])
        height = round(max(random.uniform(-50, 100), 0), 2)  # height can't be negative
        distance = random.randint(1, 100)
        angle = round(random.uniform(0, 90), 2)
        velocity = round(random.uniform(0, 100), 2)
        mass = round(random.uniform(0.1, 10), 2)

        return CannonVariables(color, height, distance, angle, velocity, mass)
