from typing import Any

from .variables import CannonVariables
from src.manual import Manual
from src.cipher import NumericCipher

COLORS =["red", "blue", "green", 'yellow', 'purple', 'black']

class CannonManual(Manual):
    def __init__(self, cfg: CannonVariables):
        super().__init__("Cannon")
        self.cfg = cfg
        
        self.ciphers = {
            color: NumericCipher()
            for color in COLORS
        }
        self.ciphers[cfg.color] = NumericCipher(seed=int(cfg.distance))

    def expert_tool_instructions(self) -> str:
        return (
            "Available Expert tools: python_interpreter(code), "
            "view_cipher(color). "
            "Use view_cipher with a single color name to retrieve only that color's mapping."
        )

    def _view_cipher(self, arguments: dict[str, Any]) -> str:
        color = arguments.get("color")
        if not isinstance(color, str) or not color.strip():
            return "view_cipher error: missing non-empty 'color'"

        normalized = color.strip().lower()
        if normalized not in self.ciphers:
            options = ", ".join(COLORS)
            return f"view_cipher error: unknown color '{normalized}'. Valid colors: {options}"

        mapping = self.ciphers[normalized].display_mapping()
        return f"{normalized} cipher mapping:\n{mapping}"
        
    def content(self):
        physics_info = """Use projectile motion to estimate the landing distance.

        If the cannon has initial height h above the floor, launch speed v, and angle theta,
        then a practical model is:
        - g = 9.81 m/s^2
        - vx = v * cos(theta)
        - vy = v * sin(theta)
        - time of flight t = (vy + sqrt(vy^2 + 2gh)) / g
        - range = vx * t
        So you can compute theta as theta = arctan((v^2 ± sqrt(v^4 - g*(g*h^2 + 2*h*v^2 - target_distance^2))) / (g*target_distance))

        For h = 0, this reduces to the familiar flat-ground formula:
        theta = 0.5 * arcsin((g * target_distance) / v^2)
        
        You can, and should, use the python_interpreter expert tool to implement these calculations and find the best angle to hit the target distance decoded from the cipher.
        """
        
        cipher_info = """On the cannon side the driver will find a ciphered message. It's actually the target distance you need to hit.
        Decode it with the cipher that matches the cannon color.

        Cipher mappings are not included by default.
        Use expert tool view_cipher(color) to request one specific color mapping at a time.
        """
        
        return f"""
        CANNON MANUAL

        Goal:
        Pick one firing angle so the projectile lands at the hidden target distance.
        This is a one-shot solution: there is no retry or post-shot adjustment.
        A run is successful when landing error is within 1% error of the target distance.

        What the Driver can observe:
        - Cannon color
        - Ciphered text on the cannon side
        - Cannon height above ground
        - Projectile launch velocity

        How to solve:
        1. Identify the cannon color.
        2. Use that color's cipher to decode the target distance from the cannon-side text.
        3. Use the physics model below with observed velocity and height to estimate a firing angle.
        4. Have the Driver set that angle (note this will also shoot the projectile) and hope for a successful hit (you only get one shot).

        {physics_info}

        {cipher_info}
        """

    def execute_expert_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if name == "python_interpreter":
            return self.execute_python_interpreter(arguments)
        if name == "view_cipher":
            return self._view_cipher(arguments)
        return f"Unknown or disallowed expert tool: {name}"
        
        