# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Fork of Agentless (LLM pipeline that localizes and repairs SWE-bench issues). Full stage-by-stage commands are in @README_swebench.md.

## Setup and running

- Not an installed package: scripts only work with the repo root on the path — `export PYTHONPATH=$PYTHONPATH:$(pwd)`. Run stages by file path, e.g. `python agentless/fl/localize.py ...`.
- API keys: `openai` backend reads `OPENAI_API_KEY`; `anthropic` reads `ANTHROPIC_API_KEY`; `deepseek` reuses the OpenAI client with `base_url="https://api.deepseek.com"`, so it **also reads `OPENAI_API_KEY`** (no separate DeepSeek variable).
- Runs on this machine are single-instance only: use `--target_id <instance_id>` (e.g. `django__django-10914`). Use `--mock` on `localize.py` to count prompt tokens without calling any API — the cheapest way to check a change.
- Regression/reproduction test stages need Docker and the SWE-bench harness.
- Set `PROJECT_FILE_LOC` to a directory of pre-computed repo structures (`<instance_id>.json`); otherwise repos are cloned into `playground/` and parsed, which is slow.

## Models

- `agentless/util/model_registry.py` is the single source of truth: model IDs, backend, `supports_temperature`, and price. CLI `--model`/`--backend` choices, `check_backend()`, the temperature gating in `agentless/util/api_requests.py`, and `dev/util/cost.py` all read from it. Add or change models there, not in individual scripts.
- Provider model names change often and older IDs get retired. Never write a model ID from memory — verify it against the provider's current docs first.
- Migration to current models is in progress on `update/apifix` (phased: shared groundwork, then DeepSeek, OpenAI, Anthropic).

## Code style and checks

- black (22.6.0) + isort (`--profile black`) via pre-commit; enable with `pre-commit install`.
- There is no unit test suite or CI. `agentless/test/` contains pipeline stages that run SWE-bench tests, not tests of this code.

## Git

- Work on topic branches (e.g. `update/apifix`) and merge to `main` through a PR.
- Working tree is CRLF while the index is LF, so `git status` shows most files as modified. Use `git diff --ignore-cr-at-eol` to see real changes.
- `.gitignore` ignores all `*.json`, `*.jsonl`, `results/`, `logs/`, and `dev/` — new files matching these stay untracked unless force-added with `git add -f` (already-tracked files like `dev/util/cost.py` are unaffected).
