from __future__ import annotations

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
    for file_path in sorted(run_dir.glob("*.json"), reverse=True):
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

    selection = st.selectbox(
        "Inspect run",
        options=[row[0].name for row in runs],
        index=0,
    )
    selected_path = run_dir / selection
    selected_payload = _load_run(selected_path)
    if not isinstance(selected_payload, dict):
        st.error("Selected run could not be loaded.")
        st.stop()
        return
    payload: dict[str, Any] = selected_payload

    result_data = _safe_get(payload, "result", default={})
    metadata = _safe_get(payload, "metadata", default={})

    st.subheader("Final Outcome")
    out1, out2, out3 = st.columns(3)
    out1.metric("Solved", str(_safe_get(result_data, "solved", default=False)))
    out2.metric("Reason", str(_safe_get(result_data, "reason", default="unknown")))
    out3.metric("Turns", str(_safe_get(result_data, "turns", default=0)))

    st.subheader("Run Metadata")
    st.json(metadata)

    st.subheader("System Prompts")
    driver_prompt = _safe_get(result_data, "driver_system_prompt", default="")
    expert_prompt = _safe_get(result_data, "expert_system_prompt", default="")
    if not driver_prompt:
        driver_prompt = _safe_get(result_data, "driver_messages", default=[{}])[0].get(
            "content", ""
        ) if isinstance(_safe_get(result_data, "driver_messages", default=[]), list) else ""
    if not expert_prompt:
        expert_prompt = _safe_get(result_data, "expert_messages", default=[{}])[0].get(
            "content", ""
        ) if isinstance(_safe_get(result_data, "expert_messages", default=[]), list) else ""

    col_driver, col_expert = st.columns(2)
    with col_driver:
        st.markdown("**Driver System Prompt**")
        st.code(driver_prompt or "(not available in this run file)")
    with col_expert:
        st.markdown("**Expert System Prompt**")
        st.code(expert_prompt or "(not available in this run file)")

    st.subheader("Agent Messages")
    msg_view = st.radio(
        "Message view",
        options=["driver", "expert", "both"],
        horizontal=True,
    )
    driver_messages = _safe_get(result_data, "driver_messages", default=[])
    expert_messages = _safe_get(result_data, "expert_messages", default=[])

    if msg_view in {"driver", "both"}:
        st.markdown("**Driver Message History**")
        if isinstance(driver_messages, list) and driver_messages:
            st.json(driver_messages)
        else:
            st.write("No saved driver messages for this run.")

    if msg_view in {"expert", "both"}:
        st.markdown("**Expert Message History**")
        if isinstance(expert_messages, list) and expert_messages:
            st.json(expert_messages)
        else:
            st.write("No saved expert messages for this run.")

    st.subheader("Tools Called")
    transcript = _safe_get(result_data, "transcript", default=[])
    tool_rows = _extract_tool_rows(transcript if isinstance(transcript, list) else [])
    if tool_rows:
        st.dataframe(tool_rows, width="stretch")
    else:
        st.write("No tool calls captured in this run.")

    st.subheader("Turn Transcript")
    if isinstance(transcript, list) and transcript:
        for turn in transcript:
            turn_id = turn.get("turn", "?") if isinstance(turn, dict) else "?"
            with st.expander(f"Turn {turn_id}", expanded=False):
                st.json(turn)
    else:
        st.write("No transcript entries available.")


if __name__ == "__main__":
    main()
