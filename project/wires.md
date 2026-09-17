# Task Specification: THE-WIRES-01

## 1. Metadata
- **Type:** Asymmetric Logic Puzzle
- **Difficulty:** Easy-Medium
- **Theme:** Inspired by "On the Subject of Wires"

## 2. Global Variables
- **`V_wires`**: Ordered wire colors (3 to 6 total), top to bottom.
- **`V_serial_last_digit`**: Integer in [0-9].
- **`V_battery_count`**: Integer battery count.
- **`V_car_lit`**: Whether the CAR indicator is lit.
- **`V_parallel_port`**: Whether a parallel port is present.

## 3. Driver Perspective (Environment Observation)
The Driver can see the module and inspect only environment locations:
- `inspect("wire panel")`: ordered wire colors with positions.
- `inspect("serial plate")`: last serial digit.
- `inspect("battery tray")`: battery count.
- `inspect("indicator strip")`: CAR indicator state.
- `inspect("port panel")`: parallel-port presence.

The Driver has no access to rule logic, only observations and action execution.

## 4. Expert Perspective (Manual)
The Expert has the rulebook for selecting one wire position based on:
- ordered colors,
- serial parity,
- and conditional overrides using battery/indicator/port data.

The Expert cannot inspect the world directly and must request exact values from the Driver.

## 5. Short Interaction Example
1. **Driver:** "I see 6 wires: 1 white, 2 blue, 3 red, 4 blue, 5 black, 6 yellow."
2. **Expert:** "Need serial last digit, CAR indicator, battery count, and parallel port."
3. **Driver:** "Serial ends in 4, CAR is off, batteries 1, parallel port present."
4. **Expert:** "Six wires + parallel port + at least two blue wires triggers override. Cut wire 2."
5. **Driver:** "Cutting wire 2."

## 6. Protocol Notes
- Text-only and turn-based by construction.
- Strict asymmetry: Driver has observations/actions, Expert has logic only.
- Requires clarification loops; omission of one variable can change the result.
- Suitable for heterogeneous-agent studies on communication precision and information decay.
