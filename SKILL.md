---
name: wenwengu-cli
description: "Local valuation workflow for the packaged wenwengu valuation engine. Use when Codex needs to run stock valuation, check runtime diagnostics, or operate the packaged valuation engine with user-configured database or Tushare settings."
metadata:
  {
    "openclaw":
      {
        "always": true,
        "skillKey": "wenwengu-cli",
        "primaryEnv": "DATABASE_URL",
        "emoji": "📈",
        "homepage": "https://github.com/huliux/wenwengu-cli-skill",
      },
  }
---

# Wenwengu CLI

## Overview

Use this skill when the user wants to:

- run a local stock valuation with the packaged `wenwengu-cli` engine
- check whether the local valuation environment is ready
- install, repair, or upgrade the packaged valuation engine
- generate a reproducible `request.json` for complex assumptions
- compare scenarios or compare two saved valuation results

This public skill is valuation-only.
It can read from a user-configured database or from Tushare, depending on runtime env.
Do not route the user into stock screening, screener cache refresh, local repo setup, or ad hoc Python scripts.

Users will speak in natural language.
Translate the intent into the closest stable workflow instead of asking the user to speak in CLI flags.

## Engine Resolution

Entrypoint priority:

1. `--bin`
2. `WENWENGU_CLI_BIN`
3. OpenClaw runtime layout
4. Codex runtime layout
5. Automatic engine install into the matching runtime path

If no engine is installed, `doctor.py`, `run_valuation.py`, and `run_cli.py`
will try to install it automatically before the real command runs.

Use [references/engine_install.md](references/engine_install.md) for install and upgrade details.

## High-Frequency Wrappers

- [scripts/install_engine.py](scripts/install_engine.py)
- [scripts/check_engine.py](scripts/check_engine.py)
- [scripts/upgrade_engine.py](scripts/upgrade_engine.py)
- [scripts/doctor.py](scripts/doctor.py)
- [scripts/make_request.py](scripts/make_request.py)
- [scripts/run_valuation.py](scripts/run_valuation.py)
- [scripts/explain_request.py](scripts/explain_request.py)
- [scripts/run_scenarios.py](scripts/run_scenarios.py)
- [scripts/compare_results.py](scripts/compare_results.py)
- [scripts/summarize_output.py](scripts/summarize_output.py)
- [scripts/run_cli.py](scripts/run_cli.py)

Use `run_cli.py` only for uncommon flag combinations not already covered by the
specialized wrappers.

## OpenClaw Agent Contract

When running inside OpenClaw, follow these rules strictly:

- Always run commands from the skill root with relative paths, for example:
  - `python scripts/doctor.py --summarize`
  - `python scripts/run_valuation.py --ts-code <ts_code> --summarize`
- Prefer wrapper scripts over direct binary invocation.
- Keep this skill valuation-only.
- Respect user-provided `DATA_SOURCE`, `DATABASE_URL`, and `DB_*` env values. Do not force Tushare.
- Do not ask users to clone any local repo.
- Do not ask users to provide CLI flags directly; translate natural language into commands.

Session behavior:

1. If session health is unknown, run `doctor.py --summarize` first.
2. If doctor fails on env/config, return exact OpenClaw config commands.
3. After user changes OpenClaw env/config, remind to:
   - `openclaw gateway restart`
   - start a new OpenClaw conversation/session
4. For regular valuation requests, default to `--summarize` unless user asks for raw JSON.

Failure recovery:

- If valuation fails with `无法找到有效的股票代码匹配`:
  1. run `python scripts/upgrade_engine.py`
  2. rerun the same valuation once
  3. if still failing, return concise blocker + request payload for debugging

## Natural-Language Routing

Map user intent to the nearest stable workflow:

- "先看看本地能不能跑", "检查 token", "环境有没有问题" -> `doctor.py`
- "把 skill 装好", "安装估值引擎", "修一下本地安装" -> `install_engine.py`
- "检查 CLI 装好了没", "现在能不能跑" -> `check_engine.py`
- "升级到最新估值引擎", "更新 CLI" -> `upgrade_engine.py`
- "给茅台跑一个标准估值" -> `make_request.py --preset base`, then `run_valuation.py --summarize`
- "乐观点", "悲观点", "保守点", "高增长", "成熟稳定" -> map to a valuation preset
- "跑三种情景", "给我 base/bull/bear" -> `run_scenarios.py`
- "做标准敏感性分析" -> add a sensitivity preset, then `run_valuation.py`
- "解释这个 request.json" -> `explain_request.py`
- "比较两个结果", "基准和保守差多少" -> `compare_results.py`
- "给某只股票做高增长 DCF" -> `make_request.py --preset high-growth --ts-code <ts_code>`, then `run_valuation.py --summarize`
- "按永续增长做敏感性" -> prefer `wacc-pgr-standard`
- "按退出乘数做敏感性" -> prefer `wacc-exit-standard`

When mapping fuzzy phrases to presets, use [references/presets.md](references/presets.md).
When the user's wording is conversational or underspecified, use [references/dialogue_examples.md](references/dialogue_examples.md).
When reporting results back to the user, use [references/output_templates.md](references/output_templates.md).

Safest defaults:

- valuation preset -> `base`
- scenario matrix -> `base,bull,bear`
- sensitivity preset without terminal-value context -> `wacc-exit-standard`
- summary output -> `--summarize`

## Core Workflow

1. Run `doctor` first when environment health is unknown.
2. Run `valuate` for a standard single-stock valuation.
3. Promote to `request.json` when assumptions become non-trivial.
4. Use `run_scenarios.py` or `compare_results.py` when the user wants side-by-side analysis.

Do not ask the user to rewrite the request in CLI syntax.
Do not dump raw JSON unless the user explicitly asked for it.
Lead with the conclusion, then the key numbers, then warnings or caveats.

## CLI Usage Surface

Use the wrappers in this skill as the primary entrypoint:

```bash
TS_CODE="<ts_code>"
python scripts/run_cli.py doctor --output json
python scripts/run_valuation.py --ts-code "$TS_CODE" --forecast-years 5 --output table
python scripts/run_valuation.py --request-file request.json --output json --save-json ./outputs/result.json
python scripts/run_valuation.py --request-file request.json --set beta=1.10 --set exit_multiple=7.0 --output json
```

Use direct flags for simple requests:

- `--ts-code`
- `--valuation-date`
- `--forecast-years`
- `--ltm-baseline`
- `--request-file`
- `--set`
- `--output`
- `--save-json`

Placeholder note:

- `<ts_code>` is a placeholder. Replace it with a real stock code before running.

Use `request.json` or `--set` for advanced assumptions such as WACC overrides,
terminal value choices, or sensitivity matrices.

Ready-to-edit templates live under:

- `templates/request/base_request.json`
- `templates/request/conservative_request.json`
- `templates/request/sensitivity_wacc_exit_standard.json`
- `templates/request/ui_full_example.json`

## Parameter System

Parameter support is complete at the request-model level.
The valuation engine exposes a small set of shell flags and accepts all advanced valuation
assumptions through `request.json` or `--set dotted.path=value`.

Read [references/valuation_parameters.md](references/valuation_parameters.md) for:

- what each valuation parameter does
- whether it is a direct shell flag or a request field
- common combinations
- recommended starting combinations
- sensitivity matrix patterns
- output section mapping from JSON to the frontend sections
- ready-to-edit request template paths

## Result Sections

The valuation response contains three top-level keys:

- `stock_info`
- `valuation_results`
- `error`

The user-facing sections you care about map like this:

- basic info -> `stock_info`
- valuation result -> `valuation_results.dcf_forecast_details`
- sensitivity matrix -> `valuation_results.sensitivity_analysis_result`
- historical financial summary -> `valuation_results.historical_financial_summary`
- historical financial ratios -> `valuation_results.historical_ratios_summary`
- forecast details -> `valuation_results.detailed_forecast_table`

## Safety Boundaries

- This public skill is valuation-only and supports runtime-selected data sources.
- Do not assume a local project checkout is required.
- Do not route the user into screening or data-refresh commands.
- Prefer saving results to external JSON files with `--save-json` instead of inventing local cache flows.

## Common Commands

### `doctor`

Use to verify the active valuation data source:

- `DATABASE_URL` or `DB_*` connectivity when `DATA_SOURCE=postgres`
- `TUSHARE_TOKEN` connectivity when `DATA_SOURCE=tushare`

Examples:

```bash
python scripts/doctor.py
python scripts/doctor.py --summarize
python scripts/run_cli.py doctor --output table
```

OpenClaw database setup (recommended):

```bash
openclaw config set skills.entries.wenwengu-cli.primaryEnv "DATABASE_URL"
openclaw config set skills.entries.wenwengu-cli.env.DATABASE_URL "postgresql://user:password@host:5432/dbname"
openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "postgres"
openclaw gateway restart
```

Alternative Tushare setup:

```bash
openclaw config set skills.entries.wenwengu-cli.env.TUSHARE_TOKEN "your_tushare_token"
openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "tushare"
openclaw gateway restart
```

After env changes, start a new OpenClaw conversation/session before re-running valuation.

### `install_engine`

Examples:

```bash
python scripts/install_engine.py
python scripts/install_engine.py --version v1.0.0
python scripts/install_engine.py --layout codex
```

### `check_engine`

Examples:

```bash
python scripts/check_engine.py
python scripts/check_engine.py --output json
```

### `upgrade_engine`

Examples:

```bash
python scripts/upgrade_engine.py
python scripts/upgrade_engine.py --version v1.0.0
```

### `valuate`

Use for single-stock valuation runs.

Examples:

```bash
TS_CODE="<ts_code>"
python scripts/run_valuation.py --ts-code "$TS_CODE" --forecast-years 5
python scripts/run_valuation.py --ts-code "$TS_CODE" --forecast-years 5 --summarize
python scripts/run_valuation.py --request-file request.json
python scripts/run_valuation.py --request-file request.json --set beta=1.10 --set exit_multiple=7.0
```

Promote the request to `request.json` when any of these are true:

- more than three business or valuation overrides are needed
- sensitivity analysis is requested
- nested dotted keys are required
- the user wants a reproducible saved scenario
- the user wants to compare scenarios later

### `make_request`

Use for complex valuation scenarios that should become a reproducible `request.json`.

Examples:

```bash
TS_CODE="<ts_code>"
python scripts/make_request.py --preset base --ts-code "$TS_CODE" --temp-file
python scripts/make_request.py --preset conservative --ts-code "$TS_CODE" --sensitivity-preset wacc-exit-standard --temp-file
python scripts/make_request.py --ts-code "$TS_CODE" --terminal-value-method perpetual_growth --perpetual-growth-rate 0.025 --beta 1.10 --output-file ./requests/request.json
python scripts/make_request.py --base-request request.json --set sensitivity_analysis.row_axis.values=[0.0509,0.0559,0.0609,0.0659,0.0709]
```

Typical flow:

1. Generate a request file with `make_request.py`.
2. Run `run_valuation.py --request-file <file>`.
3. Save the result with `--save-json` if the user will compare or revisit it.

If the user only wants a starter file, prefer the bundled templates first and
only generate a new request with `make_request.py` when the templates are not a
good fit.

### `explain_request`

Examples:

```bash
python scripts/explain_request.py --input request.json
```

### `run_scenarios`

Examples:

```bash
TS_CODE="<ts_code>"
python scripts/run_scenarios.py --ts-code "$TS_CODE"
python scripts/run_scenarios.py --ts-code "$TS_CODE" --scenarios base,conservative,bull
python scripts/run_scenarios.py --ts-code "$TS_CODE" --sensitivity-preset wacc-exit-standard
```

### `compare_results`

Examples:

```bash
python scripts/compare_results.py --left base.json --right conservative.json --left-label 基准 --right-label 保守
```
