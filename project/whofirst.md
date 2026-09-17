# Task Specification: WHOFIRST-01

## 1. Metadata
- Type: Asymmetric language/logic puzzle
- Difficulty: Medium

## 2. Global Variables (The "Knobs")
- V_rounds: Ordered round configs (default 3 rounds).
- V_display_r: Display word for round r.
- V_labels_r: Six button labels for round r, ordered positions 1..6.

## 3. Driver Perspective (Environment Observation)
The Driver can inspect only environment text and perform button presses.

Driver tools:
- inspect(place):
  - display: current display word.
  - button panel: six labeled buttons with 1-based positions.
  - progress: current round out of total rounds.
- press_whofirst_button(position): press one button (1..6) for current round.

The Driver has no manual rules and cannot infer the correct button reliably alone.

## 4. Expert Perspective (The Manual)
The Expert has the Who's on First rulebook but no environment visibility.

Manual procedure per round:
1. Use display word to map to a read-position.
2. Read the label at that position.
3. Use that label's priority list.
4. Choose the first listed word present in the current six labels.

Expert tools:
- python_interpreter(code): optional helper to automate lookup.

The Expert cannot solve without Driver-transcribed words and positions.

## 5. Interaction Example (Short)
1. Driver: "Display is 'SAYS'. Labels are 1:'READY', 2:'FIRST', 3:'HOLD', 4:'UHHH', 5:'NO', 6:'WHAT'."
2. Expert: "For SAYS, read position 6 -> WHAT. Priority for WHAT is [UHHH, WHAT]. Press button 4."
3. Driver: "Pressed 4, correct. Round advanced."
