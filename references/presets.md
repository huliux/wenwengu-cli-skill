# Presets

## Natural-language mapping

Use these mappings when the user speaks in natural language instead of naming a preset directly.

### Valuation presets

- `base`
  Aliases: `默认`, `基准`, `基础`, `标准`
- `bull`
  Aliases: `乐观`, `看多`, `牛市`, `optimistic`
- `bear`
  Aliases: `悲观`, `看空`, `熊市`, `pessimistic`
- `conservative`
  Aliases: `保守`, `谨慎`, `稳健`
- `high-growth`
  Aliases: `高增长`, `成长`
- `mature-stable`
  Aliases: `成熟`, `成熟稳定`, `稳定`

### Sensitivity presets

- `wacc-exit-standard`
  Use when the user asks for a standard exit-multiple sensitivity matrix.
- `wacc-pgr-standard`
  Use when the user asks for a standard perpetual-growth sensitivity matrix.
- `wacc-exit-wide`
  Use when the user wants a wider exit-multiple grid.
- `wacc-pgr-wide`
  Use when the user wants a wider perpetual-growth grid.

## Selection guidance

- If the user says "先来一个标准估值", start with `base`.
- If the user says "给我乐观点/保守点", map to `bull` or `conservative`.
- If the user says "跑三种情景", default to `base,bull,bear`.
- If the user asks for "标准敏感性分析" and terminal value is not specified, prefer `wacc-exit-standard`.
- If the user already chose perpetual growth, prefer `wacc-pgr-standard`.
