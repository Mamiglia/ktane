from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .types import RunResult


def save_result_json(
    result: RunResult,
    driver_model: str,
    expert_model: str,
    seed: int | None,
    temperature: float,
    max_turns: int,
    max_messages_per_agent: int,
    output_path: str | None = None,
) -> Path:
    """Persist a run result to JSON and return the written path."""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = Path("runs")
        run_dir.mkdir(parents=True, exist_ok=True)
        output = run_dir / f"{result.puzzle}_{timestamp}.json"
    else:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "puzzle": result.puzzle,
            "driver_model": driver_model,
            "expert_model": expert_model,
            "seed": seed,
            "temperature": temperature,
            "max_turns": max_turns,
            "max_messages_per_agent": max_messages_per_agent,
        },
        "result": asdict(result),
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output
