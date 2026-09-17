
# Protocol for Asymmetric LLM Cooperation Games

## 1. Core Principles
- **Strict Asymmetry:** Knowledge and Action are mutually exclusive.
- **Turn-Based/Asynchronous:** No real-time requirement. Agents take turns in a chat log.
- **Text-Only:** All environmental descriptions and instructions must be conveyed via text.
- **Non-Solvability:** The "Driver" has no logic/rules; the "Expert" has no environment access. If either agent's prompt was given to a single LLM, it should be impossible to solve without the other's specific input.

---

## 2. Role Definitions

### A. The Driver (The Eyes & Hands)
- **Environment Access:** Receives the "Observation" (textual description of the room/object). Can get further details about the environment with `inspect()` function, ex: `inspect("cannon side")`
- **Tool Access:** Can execute environment-changing commands (e.g., `set_angle()`, `push_button()`).
- **Constraint:** Has **zero** knowledge of the logic or rules. Symbols and colors are meaningless to the Driver.

### B. The Expert (The Brain)
- **Manual Access:** Receives the "Rulebook" (a long and complex set of conditional logic, mapping tables, and formulas).
- **Tool Access:** Access to a Python Interpreter for precise mathematical or logical calculations.
- **Constraint:** Has **zero** visibility of the environment. Does not know which object exists or which symbols are present until the Driver describes them.

---

## 3. Mandatory Puzzle Design Patterns
Every quiz must implement at least two of these patterns to ensure communication depth:

### Pattern 1: The Conditional Branch (The "If-Then" Trap)
- **Design:** The Manual contains rules for N different attributes of an object. The Driver sees only 1 attribute (ex: color is green).
- **Requirement:** The Expert must ask for the color, or the Driver must proactively describe it. If the Expert guesses, the probability of failure is high.

### Pattern 2: Symbolic Mapping (The "Cipher")
- **Design:** The environment contains abstract symbols (e.g., `§, %, &`). The manual contains a dictionary mapping these to numerical values.
- **Requirement:** Precise transcription. If the Driver summarizes or misses a symbol, the Expert's calculation will fail.

### Pattern 3: Missing Variables (The "Hidden Constant")
- **Design:** The final calculation requires a variable (e.g., "height from floor") that isn't in the initial observation but can be found if the Driver `inspects` the environment further.
- **Requirement:** The Expert must realize they are missing data and prompt the Driver to perform a specific action.

---

## 4. Interaction Flow (The "Handshake")

To solve a quiz, the agents must follow this minimal loop:
1. **Initial Observation:** Driver describes the high-level scene.
2. **Clarification Loop:** Expert asks for specific details (symbols, colors, dimensions) based on the Manual.
3. **Data Exchange:** Driver provides raw data; Expert uses Python to compute the solution.
4. **Execution:** Expert sends a clear command; Driver executes the tool call in the environment.

---

## 5. Success & Failure Constraints
A trial is marked as a **Failure** if:
- **Hallucination:** An agent assumes a value they cannot see/read.
- **Format Break:** The Driver fails to parse the Expert's instructions into a valid tool call.
- **Loss of Context:** In heterogeneous pairs, if one model’s verbosity causes the other to lose the "thread" of the logic.
- **Information Decay:** The Driver "simplifies" a complex symbol string (e.g., changing `ö` to `o`), making the Expert’s manual lookup fail.

---

## 6. Technical Interface
- **Communication:** Standard Chat ML (User/Assistant) format.
- **Tools:** 
  - Driver: `inspect(target)`, `action(params)`
  - Expert: `python_interpreter(code)`
- **State:** The environment state is persistent across the turn-based conversation until the "Solve" command is issued.


----
---

