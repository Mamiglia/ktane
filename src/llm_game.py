from src.game_runner import DEFAULT_MAX_TURNS, PuzzleName, Role, RunResult, run_puzzle, save_result_json
from src.game_runner.cli import build_cli_parser, main

__all__ = [
    "DEFAULT_MAX_TURNS",
    "PuzzleName",
    "Role",
    "RunResult",
    "build_cli_parser",
    "main",
    "run_puzzle",
    "save_result_json",
]


if __name__ == "__main__":
    main()
