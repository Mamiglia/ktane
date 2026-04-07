
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.manual import Manual


class Environment:
    def __init__(self, name: str, description: str, places: list):
        self.name = name
        self.description = description
        self.places = places
        self.places_info = {place: "" for place in places}
        
    def init_prompt(self):
        return f"{self.description}. You can inspect: {', '.join(self.places)}."
    
    def inspect_place(self, place: str):
        if place in self.places:
            return self.places_info[place]
        else:
            return f"{place} is not a valid place to inspect."

    def execute_driver_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        manual: Manual,
    ) -> tuple[str, bool, bool]:
        """Return (tool_result, action_attempted, solved) for a Driver tool call."""
        del manual  # Default implementation does not require manual access.
        if name == "inspect":
            place = str(arguments.get("place", "")).strip()
            if not place:
                return "inspect error: missing 'place' argument", False, False
            return self.inspect_place(place), False, False
        return f"Unknown or disallowed driver tool: {name}", False, False
        
        
    @property
    def variables(self):
        return {}
    
        