# Valuation Parameters

This file documents the packaged `wenwengu-cli` valuation interface.
The CLI is intentionally thin:

- simple runs use direct shell flags
- advanced assumptions use `request.json`
- targeted tweaks use `--set dotted.path=value`

Bundled starter templates live under:

- `templates/request/base_request.json`
- `templates/request/conservative_request.json`
- `templates/request/sensitivity_wacc_exit_standard.json`
- `templates/request/ui_full_example.json`

Placeholder note:

- `<ts_code>` is a placeholder used in docs. Replace it with a real stock code before running commands.

## 1. Quick Start

### Minimal commands

```bash
TS_CODE="<ts_code>"
python scripts/run_cli.py doctor --data-source postgres --output table
python scripts/run_valuation.py --data-source postgres --ts-code "$TS_CODE" --forecast-years 5 --output table
python scripts/run_valuation.py --data-source postgres --ts-code "$TS_CODE" --forecast-years 5 --save-json ./outputs/valuation.json --output json
```

### When to use what

- direct flags: only a few parameters changed
- `--request-file`: complex or reproducible scenarios
- `--set`: one or two precise overrides on top of a request file

### Runtime data-source configuration

Use one of these patterns before running valuation:

- database via env: set `DATABASE_URL` and optionally `DATA_SOURCE=postgres`
- database via flags: add `--data-source postgres --database-url <dsn>`
- Tushare via env: set `TUSHARE_TOKEN` and `DATA_SOURCE=tushare`

Examples:

```bash
python scripts/run_cli.py doctor --data-source postgres --database-url "postgresql://user:password@host:5432/dbname" --output json
python scripts/run_valuation.py --data-source postgres --database-url "postgresql://user:password@host:5432/dbname" --ts-code "$TS_CODE" --output table
TUSHARE_TOKEN="your_token" python scripts/run_cli.py doctor --data-source tushare --output table
```

## 2. Shell Flags

These are valuation flags available on `valuate`, typically passed through
`python scripts/run_valuation.py ...` or `python scripts/run_cli.py valuate ...`.

| Flag | Purpose | Typical use |
| --- | --- | --- |
| `--ts-code` | Stock code such as `<ts_code>` | Simple standard valuation |
| `--data-source postgres\|tushare` | Choose database-backed or Tushare-backed valuation | Control runtime data source explicitly |
| `--database-url` | Per-run PostgreSQL connection string | Avoid relying on inherited env for a single command |
| `--valuation-date` | Valuation anchor date | Backtesting or fixed-date reruns |
| `--forecast-years` | Explicit forecast horizon | Quick change from 5Y to 3Y/7Y |
| `--ltm-baseline` | Use LTM instead of latest annual report | Interim-period analysis |
| `--request-file` | Load a full valuation request JSON | Complex reproducible scenarios |
| `--set dotted.path=value` | Override any request field inline | Small targeted tweaks |
| `--output table|json|markdown` | Control output format | Human reading vs automation |
| `--save-json /path/file.json` | Save the full valuation result outside the CLI | Later comparison or downstream parsing |

Use `doctor` first if environment health is unknown:

```bash
python scripts/run_cli.py doctor --data-source postgres --output json
```

## 3. Output Sections

The valuation result maps to frontend sections as follows:

| Frontend section | JSON path |
| --- | --- |
| 基本信息 | `stock_info` |
| 估值结果 | `valuation_results.dcf_forecast_details` |
| 敏感性分析 | `valuation_results.sensitivity_analysis_result` |
| 历史财务摘要 | `valuation_results.historical_financial_summary` |
| 历史财务比率 | `valuation_results.historical_ratios_summary` |
| 预测详情 | `valuation_results.detailed_forecast_table` |
| 风险/数据警告 | `valuation_results.data_warnings` |

## 4. Request Fields by Parameter Group

### 4.1 Basic inputs

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 股票代码 | `ts_code` | Select the stock | Always required |
| 估值基准日 | `valuation_date` | Freeze the market and report date context | Fixed-date rerun |
| 使用 LTM 基期 | `ltm_baseline_enabled` | Use LTM instead of latest annual report | Interim analysis |
| 预测期年数 | `forecast_years` | Explicit DCF forecast horizon | 3Y, 5Y, 7Y |

### 4.2 Revenue assumption

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 历史 CAGR 年衰减率 | `cagr_decay_rate` | Controls how quickly historical growth decays through the forecast | `0.05` to `0.20` |

### 4.3 Margin and expense assumptions

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 营业利润率模式 | `op_margin_forecast_mode` | Margin forecast mode | `historical_median`, `transition_to_target` |
| 目标营业利润率 | `target_operating_margin` | Target EBIT margin when transitioning | request-only advanced |
| 营业利润率过渡年数 | `op_margin_transition_years` | Years to converge to target margin | request-only advanced |
| COGS 预测模式 | `cogs_forecast_mode` | Cost-of-goods forecast logic | `residual` or `direct_ratio` |
| SGA&RD 占收入比模式 | `sga_rd_ratio_forecast_mode` | SG&A + R&D ratio forecast mode | `historical_median`, `transition_to_target` |
| 目标 SGA&RD 占收入比 | `target_sga_rd_to_revenue_ratio` | Target SG&A + R&D ratio | request-only advanced |
| SGA&RD 过渡年数 | `sga_rd_transition_years` | Years to converge to target SG&A + R&D ratio | request-only advanced |

### 4.4 Asset and investment assumptions

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| D&A 占收入比模式 | `da_ratio_forecast_mode` | Depreciation/amortization ratio mode | `historical_median`, `transition_to_target` |
| 目标 D&A 占收入比 | `target_da_to_revenue_ratio` | Target D&A ratio | request-only advanced |
| D&A 过渡年数 | `da_ratio_transition_years` | Years to converge to target D&A ratio | request-only advanced |
| Capex 占收入比模式 | `capex_ratio_forecast_mode` | Capex ratio mode | `historical_median`, `transition_to_target` |
| 目标 Capex 占收入比 | `target_capex_to_revenue_ratio` | Target capex ratio | request-only advanced |
| Capex 过渡年数 | `capex_ratio_transition_years` | Years to converge to target capex ratio | request-only advanced |

### 4.5 Working-capital assumptions

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 营运资本基准口径 | `nwc_baseline_mode` | NWC baseline method | `component` recommended, `aggregate` optional |
| 核心 NWC 周转天数模式 | `nwc_days_forecast_mode` | DSO/DIO/DPO mode | `historical_median`, `transition_to_target` |
| 目标应收周转天数 | `target_accounts_receivable_days` | Target DSO | request-only advanced |
| 目标存货周转天数 | `target_inventory_days` | Target DIO | request-only advanced |
| 目标应付周转天数 | `target_accounts_payable_days` | Target DPO | request-only advanced |
| NWC 天数过渡年数 | `nwc_days_transition_years` | Years to converge to target working-capital days | `2` to `4` |
| 其他 NWC 占收入比模式 | `other_nwc_ratio_forecast_mode` | Other current assets/liabilities mode | `historical_median`, `transition_to_target` |
| 目标其他流动资产占收入比 | `target_other_current_assets_to_revenue_ratio` | Target other current assets ratio | request-only advanced |
| 目标其他流动负债占收入比 | `target_other_current_liabilities_to_revenue_ratio` | Target other current liabilities ratio | request-only advanced |
| 其他 NWC 过渡年数 | `other_nwc_ratio_transition_years` | Years to converge to target other-NWC ratios | request-only advanced |

### 4.6 Tax assumption

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 目标有效所得税率 | `target_effective_tax_rate` | Effective tax rate used in forecast FCFF | `0.20` to `0.28` |

### 4.7 WACC assumptions

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| WACC 权重模式 | `wacc_weight_mode` | Capital-structure weighting method | `market` or `target` |
| 目标债务比例 D/(D+E) | `target_debt_ratio` | Used when `wacc_weight_mode=target` | `0.20` to `0.45` |
| 税前债务成本 | `cost_of_debt` | Cost of debt before tax | `0.03` to `0.06` |
| 无风险利率 | `risk_free_rate` | Risk-free anchor | `0.02` to `0.03+` |
| Beta | `beta` | Levered beta | `0.8` to `1.3` |
| 市场风险溢价 | `market_risk_premium` | Equity market premium | `0.04` to `0.06` |
| 规模溢价 | `size_premium` | Optional small-cap premium | request-only advanced |
| 国家风险溢价 | `country_risk_premium` | Country premium | often `0` for A-share domestic base case |
| 行业风险溢价 | `industry_risk_premium` | Sector premium | optional advanced |

### 4.8 Terminal value assumptions

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 终值计算方法 | `terminal_value_method` | Terminal value method | `exit_multiple` or `perpetual_growth` |
| 退出乘数 | `exit_multiple` | EBITDA exit multiple | often `6.0` to `10.0` |
| 永续增长率 | `perpetual_growth_rate` | Long-run growth rate | often `0.02` to `0.03` |
| 启用名义 GDP 上限 | `use_gdp_cap` | Cap perpetual growth against nominal GDP anchor | `true` recommended for long-run discipline |
| 名义 GDP 上限 | `gdp_nominal_cap` | The cap value itself | often `0.05` |
| 使用年中折现 | `mid_year_convention` | Use mid-year discounting | optional for stable mature cases |

### 4.9 Sensitivity analysis

Sensitivity is configured under `sensitivity_analysis`.

| UI meaning | Request field | Purpose | Common use |
| --- | --- | --- | --- |
| 行轴参数 | `sensitivity_analysis.row_axis.parameter_name` | Row variable | `wacc`, `perpetual_growth_rate`, `exit_multiple` |
| 行轴值列表 | `sensitivity_analysis.row_axis.values` | Explicit row values | 5 or 7 values |
| 行轴步长 | `sensitivity_analysis.row_axis.step` | Optional metadata for generated grids | optional |
| 行轴点数 | `sensitivity_analysis.row_axis.points` | Optional metadata for generated grids | optional |
| 列轴参数 | `sensitivity_analysis.column_axis.parameter_name` | Column variable | `exit_multiple` or `perpetual_growth_rate` |
| 列轴值列表 | `sensitivity_analysis.column_axis.values` | Explicit column values | 5 or 7 values |
| 列轴步长 | `sensitivity_analysis.column_axis.step` | Optional metadata for generated grids | optional |
| 列轴点数 | `sensitivity_analysis.column_axis.points` | Optional metadata for generated grids | optional |

## 5. Common Combinations

### Standard baseline valuation

Use when the user says "标准估值", "先跑一个基准版".

Recommended shape:

- `forecast_years=5`
- `ltm_baseline_enabled=false`
- `op_margin_forecast_mode=historical_median`
- `cogs_forecast_mode=residual`
- `sga_rd_ratio_forecast_mode=historical_median`
- `da_ratio_forecast_mode=historical_median`
- `capex_ratio_forecast_mode=historical_median`
- `nwc_baseline_mode=component`
- `nwc_days_forecast_mode=historical_median`
- `wacc_weight_mode=market`
- `terminal_value_method=exit_multiple`

### Conservative valuation

Use when the user says "保守一点", "谨慎一点".

Recommended shape:

- baseline setup
- `terminal_value_method=perpetual_growth`
- `perpetual_growth_rate=0.02`
- `beta=1.10`
- `use_gdp_cap=true`

### Mature stable company

Use when the user says "成熟稳定", "偏长期稳态".

Recommended shape:

- `forecast_years=5`
- `terminal_value_method=perpetual_growth`
- `perpetual_growth_rate=0.02` to `0.03`
- `use_gdp_cap=true`
- optionally `mid_year_convention=true`

### High-growth company

Use when the user says "高增长", "成长股口径".

Recommended shape:

- `forecast_years=7`
- `terminal_value_method=perpetual_growth`
- `perpetual_growth_rate=0.03`
- optionally lower `cagr_decay_rate` if growth decays more slowly

### Standard sensitivity with exit multiple

Use when terminal value is based on exit multiple or not yet specified.

Recommended shape:

- row axis -> `wacc`
- column axis -> `exit_multiple`
- 5x5 grid

Example:

```json
{
  "sensitivity_analysis": {
    "row_axis": {
      "parameter_name": "wacc",
      "values": [0.0509, 0.0559, 0.0609, 0.0659, 0.0709]
    },
    "column_axis": {
      "parameter_name": "exit_multiple",
      "values": [6.0, 6.5, 7.0, 7.5, 8.0]
    }
  }
}
```

### Standard sensitivity with perpetual growth

Use when terminal value is based on perpetual growth.

Recommended shape:

- row axis -> `wacc`
- column axis -> `perpetual_growth_rate`
- 5x5 grid

## 6. Recommended Starting Patterns

If the user does not specify much, start here:

1. `doctor`
2. standard baseline valuation
3. save result with `--save-json`
4. then branch into conservative/bull/bear or sensitivity analysis

## 7. Examples

### Simple direct-run

```bash
TS_CODE="<ts_code>"
python scripts/run_valuation.py --ts-code "$TS_CODE" --forecast-years 5 --output table
```

### Save a reproducible result

```bash
TS_CODE="<ts_code>"
python scripts/run_valuation.py \
  --ts-code "$TS_CODE" \
  --forecast-years 5 \
  --output json \
  --save-json ./outputs/base-result.json
```

### Full request file close to the mobile UI

```json
{
  "ts_code": "<ts_code>",
  "valuation_date": "2026-03-16",
  "forecast_years": 5,
  "cagr_decay_rate": 0.10,
  "op_margin_forecast_mode": "historical_median",
  "cogs_forecast_mode": "residual",
  "sga_rd_ratio_forecast_mode": "historical_median",
  "da_ratio_forecast_mode": "historical_median",
  "capex_ratio_forecast_mode": "historical_median",
  "nwc_baseline_mode": "component",
  "nwc_days_forecast_mode": "historical_median",
  "nwc_days_transition_years": 3,
  "other_nwc_ratio_forecast_mode": "historical_median",
  "target_effective_tax_rate": 0.25,
  "wacc_weight_mode": "market",
  "cost_of_debt": 0.05,
  "risk_free_rate": 0.03,
  "beta": 1.00,
  "market_risk_premium": 0.05,
  "country_risk_premium": 0.0,
  "industry_risk_premium": 0.0,
  "terminal_value_method": "exit_multiple",
  "exit_multiple": 7.0,
  "use_gdp_cap": true,
  "gdp_nominal_cap": 0.05,
  "mid_year_convention": false,
  "sensitivity_analysis": {
    "row_axis": {
      "parameter_name": "wacc",
      "values": [0.0509, 0.0559, 0.0609, 0.0659, 0.0709]
    },
    "column_axis": {
      "parameter_name": "exit_multiple",
      "values": [6.0, 6.5, 7.0, 7.5, 8.0]
    }
  }
}
```

Run it with:

```bash
python scripts/run_valuation.py --request-file ./requests/request.json --output json --save-json ./outputs/result.json
```
