# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Fork of Agentless (LLM pipeline that localizes and repairs SWE-bench issues). Full stage-by-stage commands are in @README_swebench.md.

## Setup and running

- Not an installed package: scripts only work with the repo root on the path — `export PYTHONPATH=$PYTHONPATH:$(pwd)`. Run stages by file path, e.g. `python agentless/fl/localize.py ...`.
- API keys: `openai` backend reads `OPENAI_API_KEY`; `anthropic` reads `ANTHROPIC_API_KEY`; `deepseek` reuses the OpenAI client with `base_url="https://api.deepseek.com"`, so it **also reads `OPENAI_API_KEY`** (no separate DeepSeek variable).
- Retrieval (`agentless/fl/Index.py`) always calls OpenAI embeddings (`text-embedding-3-small`, hard-coded there and priced in `dev/util/cost.py`, not in the registry), so it needs a real OpenAI key in `OPENAI_API_KEY` whatever `--backend` is. With DeepSeek the key must be swapped for the retrieval stage. To skip retrieval, pass the file-level `loc_outputs.jsonl` as `--start_file` to `localize.py --related_level` instead of the `combine.py` output.
- Runs on this machine are single-instance only. Most stages take `--target_id <instance_id>` (e.g. `django__django-10914`), but `run_regression_tests.py`/`run_reproduction_tests.py` take `--instance_ids`, `rerank.py` takes `--target`, and `combine.py` has no filter. Use `--mock` on `localize.py` to count prompt tokens without calling any API — the cheapest way to check a change. A first run takes ~7 min (dataset download, repo clone, and stepping through all 300 instances on the slow `/mnt/c` filesystem), so run it in the background.
- Regression/reproduction test stages, `rerank.py --regression/--reproduction`, and final SWE-bench evaluation need Docker (from WSL: Docker Desktop with WSL integration on) and the SWE-bench harness. Localization, repair, and `rerank.py --deduplicate` (majority vote) don't.
- Set `PROJECT_FILE_LOC` to a directory of pre-computed repo structures (`<instance_id>.json`); otherwise repos are cloned into `playground/` and parsed, which is slow.
- Run the pipeline from WSL with `source .venv-wsl/bin/activate`. The Windows `.venv` can't run it: Agentless shells out to Linux commands like `rm -rf`.
- Dependencies are pinned in `requirements.txt` and tested together. Install `llama-index-core` + `llama-index-embeddings-openai` (all `agentless/fl/Index.py` uses), never the `llama-index` umbrella: it pulls `llama-index-llms-openai`, which forces `openai<3` (downgrading the `openai==3.42.1` pin) or backtracks to llama-index 0.10, which caps NumPy below 2 and breaks `pyarrow`.

## Models

- `agentless/util/model_registry.py` is the single source of truth: model IDs, backend, `supports_temperature`, and price. CLI `--model`/`--backend` choices, `check_backend()`, the temperature gating in `agentless/util/api_requests.py`, and `dev/util/cost.py` all read from it. Add or change models there, not in individual scripts.
- Provider model names change often and older IDs get retired. Never write a model ID from memory — verify it against the provider's current docs first.
- Stage defaults are legacy (`DEFAULT_MODEL` = `gpt-4o-2024-05-13`, `--backend` hard-coded to `openai`), so always pass both `--model` and a matching `--backend`; the README_swebench.md commands omit them.
- Migration to current models is in progress on `update/apifix`. Phase 0 (shared groundwork above) and Phase 1 (DeepSeek → `deepseek-flash`) are done. Phases 2 (OpenAI) and 3 (Anthropic) are paused until the full pipeline runs end-to-end with DeepSeek on one instance; Phase 4 is clean-up.
- `DeepSeekChatDecoder` always sends `extra_body={"thinking": {"type": "disabled"}}`. In non-thinking mode DeepSeek honours `temperature`, so DeepSeek keeps the original 0 / 0.8 sampling. The OpenAI/Anthropic models ignore or reject `temperature`; for them the decision is to accept less sample variety and revisit after the full pipeline works. The code still branches on the CLI temperature (`temperature == 0` asserts `num_samples == 1` in `model.py`); only the API request drops it.
- Anthropic prompt caching is broken under the pinned SDK: `api_requests.py` calls `client.beta.prompt_caching.messages.create`, which `anthropic==2.4.0` doesn't have. It runs whenever `prompt_cache=True` (repair with `--max_samples > 1`, `codegen_w_tool`). The AttributeError is swallowed by the retry loop, which waits ~2 h before returning `None`. Fix in Phase 3.

## Code style and checks

- black (22.6.0) + isort (`--profile black`) via pre-commit; enable with `pre-commit install`.
- `postprocess_data.py` shells out to `flake8` to lint patches, but flake8 isn't in `requirements.txt` or `.venv-wsl`, so the check outputs nothing and every patch "passes".
- There is no unit test suite or CI. `agentless/test/` contains pipeline stages that run SWE-bench tests, not tests of this code.

## Git

- Work on topic branches (e.g. `update/apifix`) and merge to `main` through a PR.
- Working tree is CRLF while the index is LF, so `git status` shows most files as modified. Use `git diff --ignore-cr-at-eol` to see real changes.
- `.gitignore` ignores all `*.json`, `*.jsonl`, `results/`, `logs/`, and `dev/` — new files matching these stay untracked unless force-added with `git add -f` (already-tracked files like `dev/util/cost.py` are unaffected).
