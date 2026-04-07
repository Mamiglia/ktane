from .variables import WiresVariables
from .environment import WiresEnvironment
from .manual import WiresManual

DRIVER_ACTION_NAME = "cut_wire"
DRIVER_ACTION_EXAMPLE_ARGS_JSON = '{"position": 2}'

__all__ = [
    "WiresVariables",
    "WiresEnvironment",
    "WiresManual",
    "DRIVER_ACTION_NAME",
    "DRIVER_ACTION_EXAMPLE_ARGS_JSON",
]
