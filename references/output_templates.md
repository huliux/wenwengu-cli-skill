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
3. Which fields were explicitly customized

Template:

```text
这个请求是在给 {ts_code} 做 {forecast_years} 年期 DCF 估值。
关键设定是终值法 {terminal_method}，以及 {wacc_overrides_or_none}。
这个请求里显式设置的关键字段是 {changed_fields}。
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
如果要继续执行估值，需要先修复这些项。
```

OpenClaw-specific follow-up when blocked by env:

```text
先在 OpenClaw 配置数据库连接和数据源，再重试：
openclaw config set skills.entries.wenwengu-cli.primaryEnv "DATABASE_URL"
openclaw config set skills.entries.wenwengu-cli.env.DATABASE_URL "postgresql://user:password@host:5432/dbname"
openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "postgres"
openclaw gateway restart
然后新开一个会话再跑估值。
```

## Engine Install / Upgrade

Preferred structure:

1. What install path was used
2. Whether the engine is now runnable
3. What the user should do next

Template:

```text
已把 wenwengu 估值引擎安装到 {binary_path}。
当前估值引擎 {runnable_or_not}。
下一步可以直接运行诊断或估值；如果仍然找不到引擎，再检查自动发现路径或显式指定 `WENWENGU_CLI_BIN`。
```

## Valuation Failure: Stock Match

Preferred structure:

1. State the blocker in one line
2. Trigger one repair action
3. Retry once
4. Report final state

Template:

```text
这次估值失败，阻塞点是：{error_message}。
我已执行修复：升级估值引擎并重试一次。
重试结果：{retry_result}。
如果仍失败，我会附上本次 request 供排查。
```
