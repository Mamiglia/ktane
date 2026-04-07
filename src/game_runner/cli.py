from __future__ import annotations

import argparse
import json
import os

from dotenv import load_dotenv

from .orchestrator import run_puzzle
from .puzzles import available_puzzles
from .serialization import save_result_json
from .types import DEFAULT_MAX_MESSAGES_PER_AGENT, DEFAULT_MAX_TURNS

def build_cli_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run asymmetric puzzle with LLM Driver/Expert")
    parser.add_argument("--puzzle", choices=available_puzzles(), required=True)
    parser.add_argument('--model', '-m', default="openrouter/mistralai/mistral-nemo", help="Shorthand to set both driver and expert models to the same value. Can be overridden by --driver-model and --expert-model.")
    parser.add_argument("--driver-model", type=str)
    parser.add_argument("--expert-model", type=str)
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument(
        "--max-messages-per-agent",
        type=int,
        default=DEFAULT_MAX_MESSAGES_PER_AGENT,
        help="Maximum number of successful message handoffs each agent can make.",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--print-transcript", action="store_true")
    parser.add_argument(
        "--no-json",
        action="store_false",
        dest='save_json',
        help="Save run output to a JSON file under runs/.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional explicit JSON path for run output (implies --save-json behavior when set).",
    )
    
    args = parser.parse_args()
    
    # Resolve model defaults: --model sets both, but --driver-model and --expert-model override
    if args.driver_model is None:
        args.driver_model = args.model
    if args.expert_model is None:
        args.expert_model = args.model
    
    return args


def main() -> None:
    load_dotenv()
    args = build_cli_parser()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Put it in your .env file.")

    result = run_puzzle(
        puzzle=args.puzzle,
        driver_model=args.driver_model,
        expert_model=args.expert_model,
        max_turns=args.max_turns,
        max_messages_per_agent=args.max_messages_per_agent,
        seed=args.seed,
        temperature=args.temperature,
    )

    print(f"Puzzle: {result.puzzle}")
    print(f"Solved: {result.solved}")
    print(f"Reason: {result.reason}")
    print(f"Turns: {result.turns}")

    if args.print_transcript:
        print("\\n=== Transcript ===")
        for item in result.transcript:
            print(json.dumps(item, indent=2, ensure_ascii=False))

    if args.save_json or args.output_path:
        output = save_result_json(
            result=result,
            driver_model=args.driver_model,
            expert_model=args.expert_model,
            seed=args.seed,
            temperature=args.temperature,
            max_turns=args.max_turns,
            max_messages_per_agent=args.max_messages_per_agent,
            output_path=args.output_path,
        )
        print(f"Saved run JSON: {output}")
