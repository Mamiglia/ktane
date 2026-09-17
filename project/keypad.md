# Task Specification: THE-KEYPAD-01

## 1. Metadata
- Type: Asymmetric Symbol-Matching Puzzle
- Difficulty: Medium
- Theme: Glyph matching (inspired by "On the Subject of Keypads")

## 2. Global Variables (The "Knobs")
- V_symbols: Four displayed keypad symbols (positioned 1 to 4).
- V_serial_last_digit: Last serial digit.
- V_battery_count: Number of batteries.
- V_sig_lit: Whether the SIG indicator is lit.
- V_columns: Expert-side ordered symbol columns used to derive base order.

## 3. Driver Perspective (Environment Observation)
Initial scene text indicates a keypad module with four symbol buttons and a submit switch.

Driver tools:
- inspect(place)
  - keypad: symbol list with positions 1..4
  - serial plate: last serial digit
  - battery tray: battery count
  - indicator strip: SIG lit / not lit
- press_keypad_order(order)
  - Submit one 4-step permutation of positions [1, 2, 3, 4].

Constraint: Driver has no access to the symbol-column rules.

## 4. Expert Perspective (Manual)
The Expert receives ordered symbol columns and override rules:
1. Find the single column containing all four symbols.
2. Build base order by reading those four symbols top-to-bottom in that column.
3. Apply overrides in order:
   - odd serial last digit: rotate order left by one
   - SIG lit: reverse order
   - battery count >= 3: swap second and third presses

Expert tools:
- python_interpreter(code)

Constraint: Expert cannot inspect the keypad state directly and must request exact Driver observations.

## 5. Short Interaction Example
1. Driver: "I see symbols: 1=copy, 2=trident, 3=at, 4=question."
2. Expert: "Need serial last digit, battery count, and SIG indicator state."
3. Driver: "Serial ends in 7, batteries are 2, SIG is not lit."
4. Expert: "Press positions [4, 3, 2, 1]."
5. Driver: calls press_keypad_order with that order.

This design enforces multi-turn clarification and cannot be solved from one side alone.