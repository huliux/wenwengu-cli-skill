---
name: wenwengu-cli
description: "Local CLI workflow for the wenwengu valuation repository. Use when Codex needs to run local valuation, diagnostics, stock screening, screener cache refresh, or install/upgrade/check a packaged `wenwengu-cli` binary instead of calling FastAPI directly or writing ad hoc Python. Trigger for requests like '用CLI跑估值', '跑本地估值', 'run wenwengu-cli', 'doctor/screen/data', 'refresh screener data', '检查本地环境能不能跑', '安装 wenwengu-cli', or '用本地命令行做估值'."
metadata:
  {
    "openclaw":
      {
        "always": true,
        "skillKey": "wenwengu-cli",
        "emoji": "📈",
        "homepage": "https://github.com/huliux/wenwengu-cli-skill",
      },
  }
---

# Wenwengu CLI

## Overview

Use the local CLI for this repository instead of re-implementing valuation flows in one-off scripts.
Prefer the dedicated wrapper scripts in `scripts/` for common operations. They default to machine-readable JSON output and handle repo or binary resolution.
Users will invoke this skill in natural language. Interpret the user's intent and map it to the right wrapper, preset, or comparison workflow instead of asking the user to speak in CLI flags.

Entrypoint priority:

1. If `WENWENGU_CLI_BIN` is set, or an explicit `--bin` path is provided, use the packaged binary.
2. Otherwise use `uv run --project <repo> wenwengu-cli ...`.
3. If the current directory is not inside the repo, pass `--repo` or set `WENWENGU_CLI_REPO`.

High-frequency wrappers:

- [scripts/install_binary.py](scripts/install_binary.py)
- [scripts/check_binary.py](scripts/check_binary.py)
- [scripts/upgrade_binary.py](scripts/upgrade_binary.py)
- [scripts/doctor.py](scripts/doctor.py)
- [scripts/make_request.py](scripts/make_request.py)
- [scripts/run_valuation.py](scripts/run_valuation.py)
- [scripts/explain_request.py](scripts/explain_request.py)
- [scripts/run_scenarios.py](scripts/run_scenarios.py)
- [scripts/compare_results.py](scripts/compare_results.py)
- [scripts/run_screen.py](scripts/run_screen.py)
- [scripts/run_data.py](scripts/run_data.py)
- [scripts/summarize_output.py](scripts/summarize_output.py)

Use [scripts/run_cli.py](scripts/run_cli.py) for uncommon flag combinations or commands not covered by the dedicated wrappers.

## Natural-Language Routing

Do not expect the user to name commands, presets, or files explicitly.
Translate natural-language requests into the nearest stable workflow:

- "先检查环境", "本地能不能跑", "看看 token 和数据库" -> `doctor.py`
- "把这个 skill 装好", "安装 wenwengu-cli", "装一下二进制" -> `install_binary.py`
- "检查 CLI 装好了没", "skill 现在能不能跑" -> `check_binary.py`
- "升级到最新二进制", "更新 CLI" -> `upgrade_binary.py`
- "跑一个标准估值", "先来个基准版本" -> `make_request.py --preset base`, then `run_valuation.py --summarize`
- "乐观点", "悲观点", "保守点", "高增长", "成熟稳定" -> map to the closest valuation preset
- "跑三种情景", "给我 base/bull/bear", "做情景矩阵" -> `run_scenarios.py`
- "解释这个 request.json", "这个请求里到底改了什么" -> `explain_request.py`
- "比较两个结果", "基准和乐观差多少", "哪个场景更高" -> `compare_results.py`
- "做标准敏感性分析" -> use a sensitivity preset, then `run_valuation.py`

When mapping fuzzy phrases to presets, use [references/presets.md](references/presets.md).
When the user's wording is conversational or underspecified, use [references/dialogue_examples.md](references/dialogue_examples.md) to choose the nearest workflow and default output style.
When reporting results back to the user, use [references/output_templates.md](references/output_templates.md) so the answer reads like an analysis rather than a command transcript.
If the user's phrasing is still ambiguous after reasonable inference, choose the safest default:

- valuation preset -> `base`
- scenario matrix -> `base,bull,bear`
- sensitivity preset without terminal value context -> `wacc-exit-standard`
- summary output -> `--summarize`

Keep the interaction natural-language-first:

- do not ask the user to rephrase in CLI flags
- do not dump raw JSON unless they asked for it
- prefer analytical summaries over command echoes
- lead with the conclusion, then the key numbers, then warnings or caveats

## OpenClaw Install Path

When the user is on OpenClaw, install or repair the packaged binary with
`install_binary.py`. The helper defaults to the OpenClaw runtime layout and
places the binary under `~/.openclaw/tools/wenwengu-cli/runtime/`.

Binary resolution priority:

1. `--bin`
2. `WENWENGU_CLI_BIN`
3. OpenClaw runtime path: `~/.openclaw/tools/wenwengu-cli/runtime/`
4. Codex runtime path: `~/.codex/tools/wenwengu-cli/runtime/`
5. Repo development mode: `uv run --project <repo> wenwengu-cli ...`

When the user is on OpenClaw and asks to install or repair the skill, prefer the
scripted OpenClaw-compatible layout instead of assuming the Skills UI will
surface a native installer.
Use [references/binary_install.md](references/binary_install.md) for install and upgrade details.

## Core Workflow

1. Run `doctor` first when environment health is unknown.
2. Run `valuate` for single-stock valuation work.
3. Run `screen` for Tushare-based stock screening.
4. Run `data` for screener cache status or refresh.

Prefer `--output json` when another tool, script, or agent will parse the result.
Avoid `--verbose` unless debugging, because it replays captured internal logs and print noise from the underlying pipeline.

## Safety Boundaries

Read-only commands:

- `doctor`
- `valuate`
- `screen`
- `data status`

Commands with side effects:

- `data update-stock-basic`
- `data update-daily-basic`

Do not run `data update-*` unless the user explicitly asked to refresh, update, rebuild, or repair screener cache data.
Do not silently switch `DATA_SOURCE` or change environment configuration to make a command pass.

## Commands

### `doctor`

Use to verify:

- cache directory access
- active data source readiness
- Tushare connectivity when `DATA_SOURCE=tushare`
- Postgres connectivity when `DATA_SOURCE=postgres`
- LLM key presence

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/doctor.py --repo /path/to/repo
python ~/.codex/skills/wenwengu-cli/scripts/doctor.py --repo /path/to/repo --summarize
python ~/.codex/skills/wenwengu-cli/scripts/run_cli.py doctor --output table
```

### `install_binary`

Use to install the packaged `wenwengu-cli` binary without requiring the repo checkout.
Default layout is OpenClaw-compatible and installs to `~/.openclaw/tools/wenwengu-cli/runtime/`.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/install_binary.py
python ~/.codex/skills/wenwengu-cli/scripts/install_binary.py --version v1.0.0
python ~/.codex/skills/wenwengu-cli/scripts/install_binary.py --layout codex
```

### `check_binary`

Use to verify whether the packaged binary is discoverable and runnable.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/check_binary.py
python ~/.codex/skills/wenwengu-cli/scripts/check_binary.py --output json
```

### `upgrade_binary`

Use to refresh the installed binary to the latest release or a specific tag.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/upgrade_binary.py
python ~/.codex/skills/wenwengu-cli/scripts/upgrade_binary.py --version v1.0.0
```

### `valuate`

Use for local valuation runs. The CLI reuses the repository's existing valuation pipeline.

Prefer `--request-file` for non-trivial requests.
Use `--set key=value` for targeted overrides.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/run_valuation.py --repo /path/to/repo --ts-code 600519.SH --forecast-years 3
python ~/.codex/skills/wenwengu-cli/scripts/run_valuation.py --repo /path/to/repo --ts-code 600519.SH --forecast-years 3 --summarize
python ~/.codex/skills/wenwengu-cli/scripts/run_valuation.py --request-file request.json
python ~/.codex/skills/wenwengu-cli/scripts/run_valuation.py --request-file request.json --set beta=1.15 --set terminal_value_method=\"perpetual_growth\"
```

Useful flags:

- `--request-file`
- `--ts-code`
- `--valuation-date`
- `--forecast-years`
- `--llm-summary`
- `--ltm-baseline`
- `--set dotted.key=value`
- `--output table|json|markdown`

Notes:

- Local CLI mode does not apply auth, JWT, quota, or admin APIs.
- The result payload is the same shape as the FastAPI valuation response model.

Promote the request to `--request-file` when any of these are true:

- more than three business or valuation overrides are needed
- sensitivity analysis is requested
- both LLM and valuation assumptions are being customized
- nested dotted keys are required
- the user wants a reproducible saved scenario

If the user gave multiple assumptions in prose, create a temporary JSON request file instead of forcing many flags.

### `make_request`

Use for complex valuation scenarios that should become a reproducible `request.json`.
This script can generate a request payload, apply dotted overrides, add a sensitivity template, and validate the final JSON against the repo's `StockValuationRequest` model.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/make_request.py --repo /path/to/repo --ts-code 600519.SH --forecast-years 5 --sensitivity-preset wacc-pgr-standard --temp-file
python ~/.codex/skills/wenwengu-cli/scripts/make_request.py --repo /path/to/repo --ts-code 600519.SH --terminal-value-method perpetual_growth --perpetual-growth-rate 0.025 --beta 1.1 --output-file /tmp/moutai-request.json
python ~/.codex/skills/wenwengu-cli/scripts/make_request.py --repo /path/to/repo --ts-code 600519.SH --set sensitivity_analysis.row_axis.parameter_name=wacc --set sensitivity_analysis.row_axis.values=[0.08,0.09,0.10]
python ~/.codex/skills/wenwengu-cli/scripts/make_request.py --repo /path/to/repo --preset 保守 --sensitivity-preset 标准永续增长敏感性 --ts-code 600519.SH --temp-file
```

Typical flow:

1. Generate a request file with `make_request.py`.
2. Run `run_valuation.py --request-file <file>`.
3. Add `--summarize` on the valuation step when you want a concise explanation.

Natural-language examples:

```text
"给茅台做一个保守版估值"
"做一个高增长情景，再开标准永续增长敏感性分析"
"把这个 request.json 解释一下"
```

Preferred handling:

1. Map the phrase to a preset or request workflow.
2. Generate a reproducible request file.
3. Run valuation or explanation against that file.

### `explain_request`

Use to explain an existing `request.json` in plain language, including the key changed fields relative to the model defaults.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/explain_request.py --repo /path/to/repo --input request.json
```

### `run_scenarios`

Use for multi-scenario comparisons driven by valuation presets. Default scenarios are `base,bull,bear`.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/run_scenarios.py --repo /path/to/repo --ts-code 600519.SH
python ~/.codex/skills/wenwengu-cli/scripts/run_scenarios.py --repo /path/to/repo --ts-code 600519.SH --scenarios base,conservative,bull
```

### `compare_results`

Use to compare two saved valuation result JSON payloads.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/compare_results.py --left base.json --right bull.json --left-label 基准 --right-label 乐观
```

### `screen`

Use for stock screening against merged `stock_basic + daily_basic` data from the Tushare smart-cache path.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/run_screen.py --limit 20 --pe-max 25
python ~/.codex/skills/wenwengu-cli/scripts/run_screen.py --limit 20 --pe-max 25 --summarize
python ~/.codex/skills/wenwengu-cli/scripts/run_screen.py --trade-date 20260313 --pb-max 2 --market-cap-min 100 --output table
```

Useful flags:

- `--trade-date`
- `--pe-min` / `--pe-max`
- `--pb-min` / `--pb-max`
- `--market-cap-min` / `--market-cap-max`
- `--limit`

### `data`

Use to inspect or refresh local screener cache data.

Examples:

```bash
python ~/.codex/skills/wenwengu-cli/scripts/run_data.py status
python ~/.codex/skills/wenwengu-cli/scripts/run_data.py status --summarize
python ~/.codex/skills/wenwengu-cli/scripts/run_data.py update-stock-basic --output table
python ~/.codex/skills/wenwengu-cli/scripts/run_data.py update-daily-basic --trade-date 20260313
```

Subcommands:

- `status`
- `update-stock-basic`
- `update-daily-basic`

## Execution Rules

Use `doctor` before first use in a fresh environment.
Use `--output json` for machine-readable chaining.
Use `--verbose` only when debugging a broken command.
Prefer CLI commands over importing internal modules directly when the task is operational rather than code-editing.
Prefer dedicated wrapper scripts before the generic wrapper.

Failure playbook:

- If `doctor` reports missing `TUSHARE_TOKEN`, stop Tushare-dependent commands and tell the user the token is missing.
- If `doctor` reports Postgres connectivity failure and `DATA_SOURCE=postgres`, stop and surface the connection problem instead of silently switching data sources.
- If `valuate` fails, rerun only if there is a clear parameter or environment fix. Prefer `--output json` on the retry.
- If `screen` fails after a successful `doctor`, inspect whether the failure requires `data status` or an explicit `data update-*`.

Result reporting checklist:

- For `valuate`, summarize `value_per_share`, `latest_price`, `wacc_used`, `terminal_value_method_used`, and any `data_warnings`.
- For `screen`, summarize `trade_date`, filter set, result count, and the top records shown.
- For `doctor`, summarize only failed checks unless the user asked for full status.
- For `data`, state clearly whether the command was read-only or mutating.
- For `run_scenarios` and `compare_results`, emphasize per-share value deltas, WACC changes, terminal value method changes, and warning count differences.

When a deterministic summary is useful, prefer the wrapper `--summarize` flag.
If raw JSON already exists, use [scripts/summarize_output.py](scripts/summarize_output.py) instead of reformatting by hand.
If a valuation request has many moving parts, use [scripts/make_request.py](scripts/make_request.py) instead of building a long `--set ...` chain by hand.
