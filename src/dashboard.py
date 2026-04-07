from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st  # pyright: ignore[reportMissingImports]


def _load_run(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _collect_runs(run_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    if not run_dir.exists():
        return rows
    run_files = sorted(
        run_dir.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for file_path in run_files:
        payload = _load_run(file_path)
        if payload is not None:
            rows.append((file_path, payload))
    return rows


def _safe_get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _parse_json(raw: str) -> dict[str, Any] | None:
    if not isinstance(raw, str):
        return None
    try:
        return json.loads(raw.strip())
    except Exception:
        return None


def _event_type_for_raw(parsed: dict[str, Any] | None, raw: str) -> str:
    if parsed is None:
        return "just-text"
    tool_calls = parsed.get("tool_calls")
    if tool_calls:
        return "text+tool-call"
    if parsed.get("message") or parsed.get("scratchpad"):
        return "just-text"
    return "just-text"


def _build_chat_events(result_data: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    driver_prompt = _safe_get(result_data, "driver_system_prompt", default="")
    expert_prompt = _safe_get(result_data, "expert_system_prompt", default="")
    if driver_prompt:
        events.append(
            {
                "turn": 0,
                "agent": "driver_system",
                "role": "driver",
                "label": "Driver System",
                "event_type": "just-text",
                "content": driver_prompt,
                "tool_calls": [],
                "tool_result": None,
            }
        )
    if expert_prompt:
        events.append(
            {
                "turn": 0,
                "agent": "expert_system",
                "role": "expert",
                "label": "Expert System",
                "event_type": "just-text",
                "content": expert_prompt,
                "tool_calls": [],
                "tool_result": None,
            }
        )

    transcript = _safe_get(result_data, "transcript", default=[])
    if not isinstance(transcript, list):
        return events

    for turn in transcript:
        if not isinstance(turn, dict):
            continue
        turn_id = turn.get("turn", "?")

        def add_raw_event(agent_name: str, role: str, raw_key: str) -> None:
            raw_value = turn.get(raw_key, "")
            if not raw_value:
                return
            parsed = _parse_json(raw_value)
            event_type = _event_type_for_raw(parsed, raw_value)
            content_parts: list[str] = []
            if parsed is not None:
                if parsed.get("message"):
                    content_parts.append(parsed.get("message", ""))
                if parsed.get("scratchpad"):
                    content_parts.append(f"Scratchpad: {parsed.get('scratchpad')}")
            if not content_parts:
                content_parts.append(raw_value.strip())
            events.append(
                {
                    "turn": turn_id,
                    "agent": agent_name,
                    "role": role,
                    "label": role.capitalize(),
                    "event_type": event_type,
                    "content": "\n\n".join(content_parts),
                    "tool_calls": parsed.get("tool_calls", []) if parsed else [],
                    "tool_result": None,
                }
            )

        def add_message_event(agent_name: str, role: str, message_key: str) -> None:
            message_text = turn.get(message_key, "")
            if not message_text:
                return
            events.append(
                {
                    "turn": turn_id,
                    "agent": agent_name,
                    "role": role,
                    "label": role.capitalize(),
                    "event_type": "text+message",
                    "content": message_text,
                    "tool_calls": [],
                    "tool_result": None,
                }
            )

        def add_tool_results(agent_name: str, role: str, results_key: str) -> None:
            results = turn.get(results_key, [])
            if not isinstance(results, list):
                return
            for item in results:
                if not isinstance(item, dict):
                    continue
                tool = item.get("tool", {})
                name = tool.get("name", "")
                arguments = tool.get("arguments", {})
                events.append(
                    {
                        "turn": turn_id,
                        "agent": agent_name,
                        "role": role,
                        "label": role.capitalize(),
                        "event_type": "tool-response",
                        "content": item.get("result", ""),
                        "tool_calls": [{"name": name, "arguments": arguments}],
                        "tool_result": item.get("result", ""),
                    }
                )

        add_raw_event("driver", "driver", "driver_raw")
        add_message_event("driver", "driver", "driver_message")
        add_tool_results("driver", "driver", "driver_tool_results")

        add_raw_event("expert", "expert", "expert_raw")
        add_message_event("expert", "expert", "expert_message")
        add_tool_results("expert", "expert", "expert_tool_results")

    return events


def _filter_chat_events(
    events: list[dict[str, Any]],
    view_mode: str,
    categories: list[str],
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for event in events:
        if event["event_type"] not in categories:
            continue
        if view_mode == "driver" and event["agent"] == "expert_system":
            continue
        if view_mode == "expert" and event["agent"] == "driver_system":
            continue
        if view_mode == "driver" and event["event_type"] == "tool-response" and event["agent"] == "expert":
            continue
        if view_mode == "expert" and event["event_type"] == "tool-response" and event["agent"] == "driver":
            continue
        filtered.append(event)
    return filtered


def _render_chat_event(event: dict[str, Any]) -> None:
    role = event["role"]
    actor = event["label"]
    bubble_class = "driver" if role == "driver" else "expert"
    event_class = "system" if event["agent"].endswith("_system") else bubble_class
    if event["event_type"] == "tool-response":
        event_class += " tool-response"
    meta = f"{actor} · {event['event_type']} · turn {event['turn']}"
    content = html.escape(str(event["content"]))

    tool_html = ""
    if event["tool_calls"] or event["tool_result"] is not None:
        tool_html += "<div class='chat-tools-container'>"
        if event["tool_calls"]:
            tool_html += "<div class='chat-tool'><details><summary>Tool calls</summary><pre>"
            tool_html += html.escape(json.dumps(event["tool_calls"], indent=2))
            tool_html += "</pre></details></div>"
        if event["tool_result"] is not None:
            tool_html += "<div class='chat-tool'><details><summary>Tool result</summary><pre>"
            tool_html += html.escape(str(event["tool_result"]))
            tool_html += "</pre></details></div>"
        tool_html += "</div>"

    bubble_html = f"""
<div class='chat-bubble {event_class}'>
<div class='chat-meta'>{meta}</div>
<div class='chat-content'>{content}</div>
{tool_html}
</div>
"""

    if role == "expert":
        left, right = st.columns([9, 1])
        with left:
            st.markdown(bubble_html, unsafe_allow_html=True)
    else:
        left, right = st.columns([1, 9])
        with right:
            st.markdown(bubble_html, unsafe_allow_html=True)


def _extract_tool_rows(transcript: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for turn in transcript:
        if not isinstance(turn, dict):
            continue
        turn_id = turn.get("turn", "?")

        driver_results = turn.get("driver_tool_results", [])
        if isinstance(driver_results, list):
            for item in driver_results:
                if not isinstance(item, dict):
                    continue
                tool = item.get("tool", {})
                rows.append(
                    {
                        "turn": turn_id,
                        "agent": "driver",
                        "tool": tool.get("name", ""),
                        "arguments": tool.get("arguments", {}),
                        "result": item.get("result", ""),
                    }
                )

        expert_results = turn.get("expert_tool_results", [])
        if isinstance(expert_results, list):
            for item in expert_results:
                if not isinstance(item, dict):
                    continue
                tool = item.get("tool", {})
                rows.append(
                    {
                        "turn": turn_id,
                        "agent": "expert",
                        "tool": tool.get("name", ""),
                        "arguments": tool.get("arguments", {}),
                        "result": item.get("result", ""),
                    }
                )

    return rows


def main() -> None:
    st.set_page_config(page_title="KTANE Runs", layout="wide")
    st.title("KTANE Puzzle Run Dashboard")

    default_dir = str(Path("runs"))
    run_dir_input = st.sidebar.text_input("Runs directory", value=default_dir)
    run_dir = Path(run_dir_input)

    runs = _collect_runs(run_dir)
    if not runs:
        st.info("No run files found yet. Run the CLI with --save-json first.")
        st.stop()

    summary_rows: list[dict[str, Any]] = []
    solved_count = 0
    for path, payload in runs:
        solved = bool(_safe_get(payload, "result", "solved", default=False))
        solved_count += int(solved)
        summary_rows.append(
            {
                "file": path.name,
                "puzzle": _safe_get(payload, "metadata", "puzzle", default="unknown"),
                "solved": solved,
                "reason": _safe_get(payload, "result", "reason", default="unknown"),
                "turns": _safe_get(payload, "result", "turns", default=0),
                "driver_model": _safe_get(payload, "metadata", "driver_model", default=""),
                "expert_model": _safe_get(payload, "metadata", "expert_model", default=""),
                "timestamp": _safe_get(payload, "metadata", "timestamp", default=""),
            }
        )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Runs", len(summary_rows))
    col2.metric("Solved", solved_count)
    solve_rate = (solved_count / len(summary_rows)) * 100
    col3.metric("Solve Rate", f"{solve_rate:.1f}%")

    st.subheader("Run Summary")
    st.dataframe(summary_rows, width="stretch")

    selected_name = st.sidebar.selectbox(
        "Select run to visualize",
        options=[row[0].name for row in runs],
        index=0,
    )
    selected_path = run_dir / selected_name
    selected_payload = _load_run(selected_path)
    if not isinstance(selected_payload, dict):
        st.sidebar.error("Selected run could not be loaded.")
        st.stop()
        return

    result_data = _safe_get(selected_payload, "result", default={})
    metadata = _safe_get(selected_payload, "metadata", default={})
    transcript = _safe_get(result_data, "transcript", default=[])
    driver_messages = _safe_get(result_data, "driver_messages", default=[])
    expert_messages = _safe_get(result_data, "expert_messages", default=[])

    event_categories = ["just-text", "text+tool-call", "tool-response", "text+message"]
    selected_categories = st.sidebar.multiselect(
        "Show categories",
        options=event_categories,
        default=event_categories,
        help="Filter the chat stream by message type.",
    )
    view_mode = st.sidebar.radio(
        "Model view",
        options=["both", "driver", "expert"],
        index=0,
        help="Show the transcript from the perspective of a particular model.",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Run details")
    st.sidebar.write(f"**File:** {selected_name}")
    st.sidebar.write(f"**Puzzle:** {metadata.get('puzzle', 'unknown')}")
    st.sidebar.write(f"**Solved:** {result_data.get('solved', False)}")
    st.sidebar.write(f"**Reason:** {result_data.get('reason', 'unknown')}")
    st.sidebar.write(f"**Turns:** {result_data.get('turns', 0)}")
    st.sidebar.write(f"**Driver model:** {metadata.get('driver_model', '')}")
    st.sidebar.write(f"**Expert model:** {metadata.get('expert_model', '')}")
    st.sidebar.write(f"**Timestamp:** {metadata.get('timestamp', '')}")
    if metadata.get("temperature") is not None:
        st.sidebar.write(f"**Temperature:** {metadata.get('temperature')}")
    if metadata.get("seed") is not None:
        st.sidebar.write(f"**Seed:** {metadata.get('seed')}")
    if metadata.get("max_turns") is not None:
        st.sidebar.write(f"**Max turns:** {metadata.get('max_turns')}")
    if metadata.get("max_messages_per_agent") is not None:
        st.sidebar.write(f"**Max messages:** {metadata.get('max_messages_per_agent')}")
    st.sidebar.write(f"**Driver messages:** {len(driver_messages) if isinstance(driver_messages, list) else 0}")
    st.sidebar.write(f"**Expert messages:** {len(expert_messages) if isinstance(expert_messages, list) else 0}")

    st.header(f"Visualizing run: {selected_name}")

    stats_col1, stats_col2, stats_col3 = st.columns(3)
    stats_col1.metric("Solved", str(result_data.get("solved", False)))
    stats_col2.metric("Reason", str(result_data.get("reason", "unknown")))
    stats_col3.metric("Turns", str(result_data.get("turns", 0)))

    st.markdown(
        """
        <style>
        .chat-bubble { max-width: 90%; margin-bottom: 12px; padding: 12px 16px; border-radius: 18px; line-height: 1.32; white-space: pre-wrap; word-break: break-word; font-size: 0.95rem; }
        .chat-bubble.driver { margin-left: auto; background: rgba(25, 95, 175, 0.2); color: #eef6ff; border-bottom-right-radius: 4px; border: 1px solid rgba(135, 185, 255, 0.15); box-shadow: 0 2px 5px rgba(0,0,0,0.15); }
        .chat-bubble.expert { margin-right: auto; background: rgba(130, 50, 150, 0.2); color: #f8ecff; border-bottom-left-radius: 4px; border: 1px solid rgba(215, 155, 255, 0.15); box-shadow: 0 2px 5px rgba(0,0,0,0.15); }
        .chat-bubble.system { margin-right: auto; border-bottom-left-radius: 4px; background: rgba(80, 85, 95, 0.2); color: #f1f1f3; border-radius: 18px; border: 1px solid rgba(200, 205, 215, 0.15); box-shadow: 0 2px 5px rgba(0,0,0,0.15); }
        .chat-bubble.tool-response { background: rgba(120, 120, 120, 0.1); border: 1px dashed rgba(255, 255, 255, 0.15); box-shadow: none; color: #b0b0b0; }
        .chat-meta { font-size: 0.80rem; margin-bottom: 6px; color: rgba(240,240,240,0.5); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        .chat-content { margin: 0; padding: 0; }
        .chat-tools-container { display: flex; flex-direction: row; gap: 8px; margin-top: 10px; }
        .chat-tool { flex: 1; min-width: 0; padding: 8px; background: rgba(0, 0, 0, 0.25); border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); color: #c0c0c0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.8rem; }
        .chat-tool summary { cursor: pointer; font-weight: 600; margin-bottom: 4px; font-size: 0.85rem; color: #d0d0d0; outline: none; user-select: none; }
        .chat-tool pre { margin: 0; white-space: pre-wrap; overflow-x: auto; max-height: 250px; overflow-y: auto; font-size: 0.75rem; text-overflow: ellipsis; padding-top: 6px; }
        .chat-tool details { color: inherit; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Chat-style transcript")
    chat_events = _build_chat_events(result_data)
    filtered_events = _filter_chat_events(chat_events, view_mode, selected_categories)
    if filtered_events:
        for event in filtered_events:
            _render_chat_event(event)
    else:
        st.info("No chat events match the selected category and view filters.")

    st.subheader("Tool calls")
    tool_rows = _extract_tool_rows(transcript if isinstance(transcript, list) else [])
    if tool_rows:
        st.dataframe(tool_rows, width="stretch")
    else:
        st.write("No tool calls captured in this run.")

    st.subheader("Raw turn transcript")
    if isinstance(transcript, list) and transcript:
        for turn in transcript:
            turn_id = turn.get("turn", "?") if isinstance(turn, dict) else "?"
            with st.expander(f"Turn {turn_id}", expanded=False):
                st.json(turn)
    else:
        st.write("No transcript entries available.")


if __name__ == "__main__":
    main()
