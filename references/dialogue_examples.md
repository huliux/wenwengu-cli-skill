# Dialogue Examples

Use this file when the user speaks in natural language and does not name a command, wrapper, or preset explicitly.
The goal is to map intent to the nearest stable workflow without asking the user to restate the request in CLI terms.

## Core Rule

- Infer the workflow from the user's language.
- Prefer the safest default when the wording is fuzzy.
- Generate a `request.json` when the request has multiple assumptions or should be reproducible.
- Return a concise analytical summary, not the raw command line, unless the user asks for it.

## Common Requests

### Environment check

User:
`先看看本地环境能不能跑`

Route:
- `doctor.py --summarize`

Report focus:
- missing token
- broken data source
- missing LLM key only if relevant to the ask

### Skill install or repair

User:
`把这个 skill 装好`

Route:
- run `install_binary.py`
- then run `check_binary.py`

User:
`检查这个 skill 现在能不能跑`

Route:
- `check_binary.py`

User:
`升级到最新的 CLI`

Route:
- `upgrade_binary.py`
- then `check_binary.py`

### Standard valuation

User:
`给茅台先跑一个标准估值`

Route:
- `make_request.py --preset base`
- `run_valuation.py --summarize`

Defaults:
- valuation preset: `base`
- output: summary

### More optimistic or conservative

User:
`同样是茅台，给我乐观点`

Route:
- map `乐观` -> `bull`
- reuse the current stock code or request context if already established
- prefer a request file if this is a follow-up to an existing scenario

User:
`那再保守一点`

Route:
- map `保守` -> `conservative`

### Three scenarios

User:
`跑三种情景看看`

Route:
- `run_scenarios.py`
- default scenarios: `base,bull,bear`

Report focus:
- per-share value by scenario
- WACC delta
- terminal method delta
- warning count delta

### High-growth or mature company framing

User:
`按高增长公司来估一下`

Route:
- map to `high-growth`

User:
`按成熟稳定公司口径做`

Route:
- map to `mature-stable`

### Standard sensitivity analysis

User:
`做一个标准敏感性分析`

Route:
- if terminal value context is unknown, prefer `wacc-exit-standard`
- if the user already asked for perpetual growth, prefer `wacc-pgr-standard`
- build with `make_request.py`, then run valuation

### Request explanation

User:
`帮我解释一下这个 request.json`

Route:
- `explain_request.py`

Report focus:
- stock code
- valuation horizon
- terminal value method
- major overrides versus defaults

### Compare two saved results

User:
`比较一下基准和乐观结果`

Route:
- `compare_results.py`

Report focus:
- per-share value delta
- WACC delta
- terminal value method delta
- warning count delta

### Screening

User:
`筛一下 PE 小于 25 的票`

Route:
- `run_screen.py --summarize`

Report focus:
- trade date
- filter set
- result count
- top few tickers shown

### Data refresh

User:
`把筛选数据更新一下`

Route:
- this is a mutating request, so `run_data.py update-*` is allowed
- choose the narrowest refresh path implied by the request

Guardrail:
- do not run refresh commands unless the user explicitly asked to update, refresh, rebuild, or repair data

## Ambiguous Requests

### "先跑一下"

Interpretation:
- if no stock or target is known, do not guess a ticker
- ask for the missing stock code or name

### "标准版就行"

Interpretation:
- if the target stock is known, use `base`
- if the target stock is not known, ask only for the stock

### "再来个保守版"

Interpretation:
- reuse the most recent stock or request context in the conversation
- switch only the preset unless the user also changed assumptions

### "做个敏感性"

Interpretation:
- if terminal method is unknown, default to `wacc-exit-standard`
- if the current request/result already uses perpetual growth, default to `wacc-pgr-standard`

## Output Style

For natural-language users, prefer analysis-first reporting:

- what was run
- the key conclusion
- the most important drivers or warnings

Do not dump raw JSON unless the user explicitly asks for raw output.
Do not ask the user to rewrite the request in CLI syntax.
Use [output_templates.md](output_templates.md) to keep the wording analytical and conclusion-first.
