from __future__ import annotations

from typing import Any

from src.environment import Environment
from src.manual import Manual

from .model_io import litellm_chat, normalize_tool_calls, safe_json_object
from .prompts import driver_system_prompt, expert_system_prompt
from .puzzles import build_puzzle, driver_action_prompt_fields
from .types import DEFAULT_MAX_MESSAGES_PER_AGENT, PuzzleName, Role, RunResult


def _extract_message_content(arguments: dict[str, Any]) -> str:
    for key in ("content", "message", "text"):
        value = arguments.get(key)
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
    return ""


def _init_messages(
    env: Environment,
    manual: Manual,
    driver_prompt: str,
    expert_prompt: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    driver_messages: list[dict[str, str]] = [
        {"role": "system", "content": driver_prompt},
        {
            "role": "user",
            "content": (
                "Initial environment observation:\n"
                f"{env.init_prompt()}\n"
                "You can start by inspecting a place."
            ),
        },
    ]
    expert_messages: list[dict[str, str]] = [
        {"role": "system", "content": expert_prompt},
        {
            "role": "user",
            "content": "Manual content:\n" + manual.content(),
        },
    ]
    return driver_messages, expert_messages


def _empty_turn_record(turn: int, active_role: Role) -> dict[str, Any]:
    return {
        "turn": turn,
        "active_role": active_role,
        "driver_raw": "",
        "driver_message": "",
        "driver_scratchpad": "",
        "driver_tool_results": [],
        "expert_raw": "",
        "expert_message": "",
        "expert_scratchpad": "",
        "expert_tool_results": [],
    }


def _process_driver_turn(
    *,
    puzzle: PuzzleName,
    env: Environment,
    manual: Manual,
    driver_model: str,
    temperature: float,
    driver_messages: list[dict[str, str]],
    expert_messages: list[dict[str, str]],
    turn_record: dict[str, Any],
) -> tuple[bool, str, bool, bool]:
    """Return (action_attempted, reason, solved, passed_turn)."""
    del puzzle
    driver_raw = litellm_chat(driver_model, driver_messages, temperature)
    driver_data = safe_json_object(driver_raw)
    driver_scratchpad = str(driver_data.get("scratchpad", "")).strip()
    driver_tools = normalize_tool_calls(driver_data)

    driver_messages.append({"role": "assistant", "content": driver_raw})
    turn_record["driver_raw"] = driver_raw
    turn_record["driver_scratchpad"] = driver_scratchpad

    if not driver_tools:
        result = (
            "driver output error: no tool calls were provided. "
            "Call at least one tool (inspect, action, or message)."
        )
        driver_messages.append(
            {
                "role": "user",
                "content": result,
            }
        )
        turn_record["driver_tool_results"].append(
            {
                "tool": {"name": "<none>", "arguments": {}},
                "result": result,
            }
        )
        return False, "", False, False

    for call in driver_tools:
        if call["name"] == "message":
            content = _extract_message_content(call["arguments"])
            if not content:
                result = "message error: missing non-empty 'content'"
                driver_messages.append(
                    {
                        "role": "user",
                        "content": f"Driver tool result for {call['name']}:\n{result}",
                    }
                )
                turn_record["driver_tool_results"].append(
                    {
                        "tool": call,
                        "result": result,
                    }
                )
                continue

            expert_messages.append(
                {
                    "role": "user",
                    "content": f"Driver says:\n{content}",
                }
            )
            turn_record["driver_message"] = content
            result = "Message delivered to Expert. Turn passed."
            driver_messages.append(
                {
                    "role": "user",
                    "content": f"Driver tool result for {call['name']}:\n{result}",
                }
            )
            turn_record["driver_tool_results"].append(
                {
                    "tool": call,
                    "result": result,
                }
            )
            return False, "", False, True

        result, attempted_action, action_solved = env.execute_driver_tool(
            call["name"], call["arguments"], manual
        )

        driver_messages.append(
            {
                "role": "user",
                "content": f"Driver tool result for {call['name']}:\n{result}",
            }
        )
        turn_record["driver_tool_results"].append(
            {
                "tool": call,
                "result": result,
            }
        )

        if attempted_action:
            return True, ("action_solved" if action_solved else "action_failed"), action_solved, False

    return False, "", False, False


def _process_expert_turn(
    *,
    manual: Manual,
    expert_model: str,
    temperature: float,
    expert_messages: list[dict[str, str]],
    driver_messages: list[dict[str, str]],
    turn_record: dict[str, Any],
) -> bool:
    """Return True when Expert passed the turn via message tool."""
    expert_raw = litellm_chat(expert_model, expert_messages, temperature)
    expert_data = safe_json_object(expert_raw)
    expert_scratchpad = str(expert_data.get("scratchpad", "")).strip()
    expert_tools = normalize_tool_calls(expert_data)

    expert_messages.append({"role": "assistant", "content": expert_raw})
    turn_record["expert_raw"] = expert_raw
    turn_record["expert_scratchpad"] = expert_scratchpad

    if not expert_tools:
        result = (
            "expert output error: no tool calls were provided. "
            "Call at least one tool (python_interpreter or message)."
        )
        expert_messages.append(
            {
                "role": "user",
                "content": result,
            }
        )
        turn_record["expert_tool_results"].append(
            {
                "tool": {"name": "<none>", "arguments": {}},
                "result": result,
            }
        )
        return False

    for call in expert_tools:
        if call["name"] == "message":
            content = _extract_message_content(call["arguments"])
            if not content:
                result = "message error: missing non-empty 'content'"
                expert_messages.append(
                    {
                        "role": "user",
                        "content": f"Expert tool result for {call['name']}:\n{result}",
                    }
                )
                turn_record["expert_tool_results"].append(
                    {
                        "tool": call,
                        "result": result,
                    }
                )
                continue

            driver_messages.append(
                {
                    "role": "user",
                    "content": f"Expert says:\n{content}",
                }
            )
            turn_record["expert_message"] = content
            result = "Message delivered to Driver. Turn passed."
            expert_messages.append(
                {
                    "role": "user",
                    "content": f"Expert tool result for {call['name']}:\n{result}",
                }
            )
            turn_record["expert_tool_results"].append(
                {
                    "tool": call,
                    "result": result,
                }
            )
            return True

        result = manual.execute_expert_tool(call["name"], call["arguments"])
        expert_messages.append(
            {
                "role": "user",
                "content": f"Expert tool result for {call['name']}:\n{result}",
            }
        )
        turn_record["expert_tool_results"].append(
            {
                "tool": call,
                "result": result,
            }
        )
    return False


def run_puzzle(
    puzzle: PuzzleName,
    driver_model: str,
    expert_model: str,
    max_turns: int,
    seed: int | None,
    temperature: float,
) -> RunResult:
    env, manual = build_puzzle(puzzle, seed)

    driver_prompt = driver_system_prompt(puzzle)
    expert_prompt = expert_system_prompt(puzzle, manual.expert_tool_instructions())
    driver_messages, expert_messages = _init_messages(env, manual, driver_prompt, expert_prompt)

    transcript: list[dict[str, Any]] = []
    solved = False
    reason = "max_turns_reached"
    active_role: Role = "driver"
    driver_message_count = 0
    expert_message_count = 0

    for turn in range(1, max_turns + 1):
        if active_role == "driver" and driver_message_count >= max_messages_per_agent:
            reason = "driver_message_limit_reached"
            break
        if active_role == "expert" and expert_message_count >= max_messages_per_agent:
            reason = "expert_message_limit_reached"
            break

        turn_record = _empty_turn_record(turn, active_role)

        if active_role == "driver":
            attempted_action, action_reason, action_solved, driver_passed = _process_driver_turn(
                puzzle=puzzle,
                env=env,
                manual=manual,
                driver_model=driver_model,
                temperature=temperature,
                driver_messages=driver_messages,
                expert_messages=expert_messages,
                turn_record=turn_record,
            )

            if attempted_action:
                solved = action_solved
                reason = action_reason
                transcript.append(turn_record)
                return RunResult(
                    puzzle=puzzle,
                    solved=solved,
                    reason=reason,
                    turns=turn,
                    transcript=transcript,
                    driver_system_prompt=driver_prompt,
                    expert_system_prompt=expert_prompt,
                    driver_messages=driver_messages,
                    expert_messages=expert_messages,
                )

            if driver_passed:
                driver_message_count += 1
                active_role = "expert"
        else:
            expert_passed = _process_expert_turn(
                manual=manual,
                expert_model=expert_model,
                temperature=temperature,
                expert_messages=expert_messages,
                driver_messages=driver_messages,
                turn_record=turn_record,
            )
            if expert_passed:
                expert_message_count += 1
                active_role = "driver"

        transcript.append(turn_record)

    return RunResult(
        puzzle=puzzle,
        solved=solved,
        reason=reason,
        turns=max_turns,
        transcript=transcript,
        driver_system_prompt=driver_prompt,
        expert_system_prompt=expert_prompt,
        driver_messages=driver_messages,
        expert_messages=expert_messages,
    )
