# Task Specification: THE-CANNON-01

## 1. Metadata
- **Type:** Asymmetric Physics/Logic Puzzle
- **Difficulty:** Medium

## 2. Global Variables (The "Knobs")
These variables are randomized for each instance of the game:
- **`V_color`**: [Yellow | Red | Blue | Striped Yellow-Red | ...]
- **`V_height`**: Height of the cannon from the floor (meters). [float]
- **`V_mass`**: Mass of the projectile (kg). [float]
- `V_velocity`: initial velocity of the ball (m/s) [float]
- **`V_target`**: The required distance the ball must travel (meters).
- `V_mappings`: The cipher translating the symbols into numbers (and vice-versa) [dict(str: dict(char: int))]

## 3. Driver Perspective (Environment Observation)
The Driver is provided with a descriptive text of the scene:
> "A cannon [V_color] stands in front of you. It is loaded with a [V_mass]kg ball. You can set the angle of the cannon."

**Driver Tools:**
- `inspect(target)`: Get more detail on an object.
	- `height`: The cannon is positioned on a platform [V_height]m above the floor.
	- `side`: On the side of the cannon, symbols are engraved: '[V_mapping(V_target)]'.
- `set_angle(float)`: Fires the cannon at the specified angle.

## 4. Expert Perspective (The Manual)
The Expert is provided with a multi-page rulebook and a Python environment:
> **MANUAL: Projectile Regulation**
> 1. **Decode Target Distance:** Locate the color of the cannon and use the mapping table to convert symbols to a numerical distance ($d$).
>    - *If Striped Yellow-Red:* {ß:0, !:1, $:2, %:3, &:4, ~:5, ö:6, k:7, ä:8, §:9}
>    - *If Blue:* [Different Mapping...]
> 2. **Calculate Launch Angle:** Use the Python tool to solve for $\theta$. 
>    - **Formula:** $d = \frac{v^2 \sin(2\theta)}{g}$ (simplified) or use the full trajectory equation considering the height ($h$).
>    - **Constants:** Initial velocity ($v$) is fixed at V_velocity m/s. Gravity ($g$) is 9.81.

**Expert Tools:**
- `python_interpreter(code)`: Execute math to find the exact angle.

---

## 5. Standardized Interaction Example

| Turn | Role | Message | Action/Tool |
| :--- | :--- | :--- | :--- |
| 1 | **Driver** | I see a cannon striped in yellow and red. It's at 3m height. It has a 3kg ball. The side says: `%k.~ö`. What angle should I set? | *Observation* |
| 2 | **Expert** | I have the manual for striped cannons. Let me decode those symbols: `%`=3, `k`=7, `.`= (not in table), `~`=5, `ö`=6. **Wait**, Driver, what is the symbol between `k` and `~` exactly? | *Manual Lookup* |
| 3 | **Driver** | My apologies, the symbol is actually `.` which looks like a small speck. Let me look closer... it is a `.` | `inspect(side)` |
| 4 | **Expert** | The manual says the `.` is a decimal point. So the distance is $37.56$ meters. Calculating the angle now... | `python_interpreter` |
| 5 | **Expert** | Based on $d=37.56$, $h=3$, and $v=20$, you must set the angle to **28.4 degrees**. | *Response* |
| 6 | **Driver** | Setting angle to 28.4. | `set_angle(28.4)` |
