from __future__ import annotations

import json
import os
from typing import Any

import litellm
from litellm import completion

litellm.suppress_debug_info = True


def safe_json_object(text: str) -> dict[str, Any]:
    """Parse model output as JSON object with a permissive fenced-block fallback."""
    raw = text.strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

    if raw:
        return {
            "tool_calls": [
                {
                    "name": "message",
                    "arguments": {"content": raw},
                }
            ]
        }
    return {"tool_calls": []}


def normalize_tool_calls(data: dict[str, Any]) -> list[dict[str, Any]]:
    tool_calls = data.get("tool_calls", [])
    if not isinstance(tool_calls, list):
        return []

    normalized: list[dict[str, Any]] = []
    for call in tool_calls:
        if not isinstance(call, dict):
            continue
        name = call.get("name")
        arguments = call.get("arguments", {})
        if not isinstance(name, str):
            continue
        if not isinstance(arguments, dict):
            arguments = {}
        normalized.append({"name": name, "arguments": arguments})
    return normalized


def litellm_chat(
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> str:
    kwargs = {}
    if model.startswith("openrouter/"):
        kwargs["api_base"] = "https://openrouter.ai/api/v1"
        kwargs["api_key"] = os.getenv("OPENROUTER_API_KEY")
    elif model.startswith("openai/"):
        kwargs["api_base"] = os.getenv("OPENAI_API_BASE")
        kwargs["api_key"] = os.getenv("OPENAI_API_KEY", "dummy-key")

    response: Any = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs
    )
    return response.choices[0].message.content or ""
