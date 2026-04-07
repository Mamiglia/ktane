from .variables import CannonVariables
from .environment import CannonEnvironment
from .manual import CannonManual

DRIVER_ACTION_NAME = "set_angle_and_shoot"
DRIVER_ACTION_EXAMPLE_ARGS_JSON = '{"angle": 28.4}'

__all__ = [
    "CannonVariables",
    "CannonEnvironment",
    "CannonManual",
    "DRIVER_ACTION_NAME",
    "DRIVER_ACTION_EXAMPLE_ARGS_JSON",
]
