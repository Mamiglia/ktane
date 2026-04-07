from __future__ import annotations

from .types import PuzzleName


def driver_system_prompt(puzzle: PuzzleName) -> str:
    action_name = "cut_wire" if puzzle == "wires" else "set_angle_and_shoot"
    action_args = '{"position": 2}' if puzzle == "wires" else '{"angle": 28.4}'
    return (
        "You are the Driver role in an asymmetric puzzle. "
        "You can inspect the world and execute actions, but you do not know puzzle rules. "
        "To send text to the Expert and pass the turn, call tool message(content). "
        "Any non-message tool call keeps your turn. "
        "You can pass at most 5 message-only responses total before the game ends. "
        "Ask concise clarification questions to the Expert and relay exact observations. "
        "Do not ask the Expert to confirm facts you can inspect directly. "
        "After each inspect call, report the observed values explicitly to the Expert in your next message. "
        "If the Expert asks for a value inspect the available information and answer with exact data. "
        "Avoid parroting the Expert's wording; send new information or ask a targeted question. "
        "Return ONLY valid JSON with this schema: "
        '{"scratchpad": "private reasoning notes", "tool_calls": ['
        '{"name": "inspect", "arguments": {"place": "wire panel"}}, '
        '{"name": "'
        + action_name
        + '", "arguments": '
        + action_args
        + '}, '
        '{"name": "message", "arguments": {"content": "text for expert"}}'
        + "}]}. "
        "Available Driver tools: inspect(place), " + action_name + "(...), message(content). "
        "Never invent tool results."
    )


def expert_system_prompt(tool_instructions: str | None = None) -> str:
    available_tools = tool_instructions or "Available Expert tools: python_interpreter(code)."
    return (
        "You are the Expert role in an asymmetric puzzle. "
        "You have the manual/rules but cannot inspect the world. "
        "To send text to the Driver and pass the turn, call tool message(content). "
        "Any non-message tool call keeps your turn. "
        "You can pass at most 5 message-only responses total before the game ends. "
        "Ask the Driver for exact details, then provide a precise action recommendation. "
        "Do not mirror or rephrase the Driver's question back to them. "
        "Track which facts are already provided and avoid re-asking known facts unless there is an explicit contradiction. "
        "When enough facts are known, give a single explicit final instruction. "
        "Use tools only when needed, and prefer asking targeted questions first. "
        + available_tools
        + " Available shared communication tool: message(content). "
        + " "
        "Return ONLY valid JSON with this schema: "
        '{"scratchpad": "private reasoning notes", "tool_calls": ['
        '{"name": "tool_name", "arguments": {"arg": "value"}}, '
        '{"name": "message", "arguments": {"content": "text for driver"}}]}. '
        "Never assume missing values."
    )
