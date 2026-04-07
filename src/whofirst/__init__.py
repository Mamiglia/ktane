from .variables import WhofirstVariables
from .environment import WhofirstEnvironment
from .manual import WhofirstManual

DRIVER_ACTION_NAME = "press_whofirst_button"
DRIVER_ACTION_EXAMPLE_ARGS_JSON = '{"position": 2}'

__all__ = [
    "WhofirstVariables",
    "WhofirstEnvironment",
    "WhofirstManual",
    "DRIVER_ACTION_NAME",
    "DRIVER_ACTION_EXAMPLE_ARGS_JSON",
]