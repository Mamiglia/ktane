from typing import Any, Literal
import math


from src.environment import Environment
from src.manual import Manual
from .variables import CannonVariables
from src.cipher import NumericCipher

class CannonEnvironment(Environment):
    def __init__(
        self, 
        cfg: CannonVariables
    ):
        super().__init__(
            name="Cannon Environment",
            description=(
                f"You are in a big room with a {cfg.color} cannon. "
                "The cannon is aimed at the ground and can be adjusted in angle. "
                "There is a projectile loaded in the cannon."
            ),
            places=["cannon", "cannon side", "ground distance", "projectile"]
        )
        self.cfg = cfg

        self.cipher = NumericCipher(seed=int(cfg.distance))
        self.encoded_distance = self.cipher.encode(cfg.distance)

        self.places_info["cannon side"] = f"On the side of the {self.cfg.color} cannon you see writing that says: \"{self.encoded_distance}\"."
        self.places_info["ground distance"] = f"The cannon is at {self.cfg.height} meters from the ground" 
        self.places_info["projectile"] = f"The projectile has a mass of {self.cfg.mass} kg. It is currently loaded in the cannon and ready to be fired with a velocity of {self.cfg.velocity} m/s."
        self.places_info["cannon"] = f"The cannon is {self.cfg.color} and it sits at {self.cfg.height} meters above the ground. It can be aimed at an angle between 0 and 90 degrees. Setting the angle will fire the projectile and cause it to land at some distance from the base of the cannon. Note you only have one shot.\n\nYou note something written on the side ['cannon side']. If you need to estimate the projectile mass or velocity at any point, you can inspect the projectile to get that information ['projectile']."
        
    def is_solvable(self):
        # is there an angle for which the projectile will land within 1 meter of the target distance?
        for angle in range(0, 91):
            self.cfg.angle = angle
            if abs(self.range() - self.cfg.distance) <= 1.0:
                return True
        return False
        
    def range(self):
        # Projectile range from an initial height above the floor (y=0)
        g = 9.81  # gravity (m/s^2)
        angle_rad = math.radians(self.cfg.angle)

        vx = self.cfg.velocity * math.cos(angle_rad)
        vy = self.cfg.velocity * math.sin(angle_rad)

        # Solve: height + vy*t - 0.5*g*t^2 = 0  -> take positive root
        disc = vy**2 + 2 * g * self.cfg.height
        if disc < 0:
            return 0.0

        t_flight = (vy + math.sqrt(disc)) / g
        return max(0.0, vx * t_flight)

    def set_angle(self, angle: float) -> str:
        """Perform the driver action of firing the cannon at a given angle."""
        if angle < -90 or angle > 90:
            return "Invalid angle. Choose an angle between 0 and 90 degrees."

        self.cfg.angle = float(angle)
        landed = self.range()
        delta = abs(landed - self.cfg.distance)
        return (
            f"Cannon fired at {self.cfg.angle:.2f} degrees. "
            f"Projectile landed at {landed:.2f} meters. "
            f"Distance error from target is {delta:.2f} meters."
        )

    def execute_driver_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        manual: Manual,
    ) -> tuple[str, bool, bool]:
        if name == "inspect":
            return super().execute_driver_tool(name, arguments, manual)

        if name != "set_angle_and_shoot":
            return f"Unknown or disallowed driver tool: {name}", False, False

        try:
            angle = float(arguments.get("angle", 0.0))
        except (TypeError, ValueError):
            return "set_angle_and_shoot error: angle must be numeric", False, False

        result = self.set_angle(angle)
        solved = abs(self.range() - self.cfg.distance) / self.range() <= 0.01  # within 1% of target distance is considered solved
        return result, True, solved
    
