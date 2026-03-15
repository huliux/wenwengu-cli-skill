# Output Templates

Use these templates when the skill is responding to natural-language users.
The response should read like an analysis result, not like a command log.

## Global Rules

- Start with what conclusion the run supports.
- Then state the key numbers that justify the conclusion.
- Then state the main risks, warnings, or caveats.
- Do not start by echoing the command line.
- Do not paste raw JSON unless the user explicitly asked for raw output.

## Valuation

Preferred structure:

1. What was run
2. The valuation conclusion
3. Core drivers
4. Warnings

Template:

```text
对 {stock_name} ({ts_code}) 跑了 {scenario_or_request}。
结论是 DCF 每股价值 {高于/低于} 现价 {x}%。
核心参数是 WACC {wacc}、终值法 {terminal_method}、预测期 {forecast_years} 年。
需要注意的是: {warnings_or_none}
```

## Scenario Matrix

Preferred structure:

1. What scenarios were run
2. Which scenario is highest and lowest
3. How far the comparison deviates from the baseline

Template:

```text
对 {stock_name} ({ts_code}) 跑了 {scenario_list} 三组情景。
结论是 {highest_scenario} 每股价值最高，{lowest_scenario} 最低。
相对基准情景，{scenario_name} 的主要变化来自每股价值 {delta}、WACC {delta}、终值法 {delta}。
```

## Result Comparison

Preferred structure:

1. What two results are being compared
2. Whether the right side is higher or lower
3. Which key assumptions changed

Template:

```text
比较了 {left_label} 和 {right_label} 两个结果。
结论是 {right_label} 的每股价值相对 {left_label} {上升/下降} {x}%。
差异主要来自 WACC {delta}、终值法 {delta}，以及数据警告数 {delta}。
```

## Request Explanation

Preferred structure:

1. What the request is valuing
2. Which assumptions matter most
3. Which fields differ from defaults

Template:

```text
这个请求是在给 {ts_code} 做 {forecast_years} 年期 DCF 估值。
关键设定是终值法 {terminal_method}，以及 {wacc_overrides_or_none}。
相对默认请求，主要改动字段是 {changed_fields}。
```

## Doctor

Preferred structure:

1. Whether the environment is runnable
2. Which dependency blocks execution
3. What the user needs to fix

Template:

```text
环境检查结果是 {runnable_or_blocked}。
当前主要问题是 {failed_checks_or_none}。
如果要继续执行 {next_task}，需要先修复这些项。
```

## Binary Install / Upgrade

Preferred structure:

1. What install path was used
2. Whether the binary is now runnable
3. What the user should do next

Template:

```text
已把 wenwengu-cli 安装到 {binary_path}。
当前二进制 {runnable_or_not}。
下一步可以直接运行估值、筛选或诊断流程；如果仍然找不到 CLI，再检查自动发现路径或显式指定 `WENWENGU_CLI_BIN`。
```

## Screening

Preferred structure:

1. What filter was applied
2. How many records matched
3. Which results are worth looking at first

Template:

```text
按 {filters} 跑了筛选。
结果命中 {count} 条记录。
优先看这几只: {top_records_preview}
```
