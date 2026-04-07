# KTANE Asymmetric LLM Puzzles

This repository contains asymmetric Driver/Expert puzzle environments.

## Install

```bash
pip install -r requirements.txt
```

## OpenRouter setup

Create a `.env` file in the repo root:

```env
OPENROUTER_API_KEY=your_key_here
```

## Run an LLM puzzle

```bash
python -m src.llm_game --puzzle wires --seed 0 --print-transcript --save-json
```

```bash
python -m src.llm_game --puzzle cannon --seed 1 --max-turns 14 --print-transcript --save-json
```

Use `--output-path runs/my_run.json` to save to a specific file.

## Dashboard

After saving one or more runs to JSON, launch:

```bash
streamlit run src/dashboard.py
```

The dashboard reads `runs/*.json` by default and shows:
- overall solve metrics
- per-run summary table
- detailed turn-by-turn transcript viewer

## Notes

- Driver can call `inspect(...)` plus puzzle action (`cut_wire` or `set_angle`).
- Expert can call `python_interpreter(code)`.
- The host script executes tools and determines puzzle success/failure.
