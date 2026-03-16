#!/usr/bin/env python3
"""Explain a request.json in plain language."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import parse_json_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="explain_request.py",
        description="Explain a wenwengu request.json in plain language.",
    )
    parser.add_argument("--input", required=True, help="Request JSON file path.")

    args = parser.parse_args(argv)
    payload = parse_json_payload(Path(args.input).read_text(encoding="utf-8"))
    print(explain_request_payload(payload))
    return 0


def explain_request_payload(payload: dict[str, Any]) -> str:
    ts_code = payload.get("ts_code", "N/A")
    changed_fields = _collect_changed_paths(payload, {})

    sensitivity = payload.get("sensitivity_analysis") or {}
    row_axis = sensitivity.get("row_axis") or {}
    column_axis = sensitivity.get("column_axis") or {}

    lines = [
        "请求摘要",
        "- 结论: "
        f"这是一个针对 {ts_code} 的 "
        f"{payload.get('forecast_years', 'N/A')} 年期 DCF 请求。",
        f"- 标的: {ts_code}",
        f"- 估值日: {payload.get('valuation_date') or '最新可用日期'}",
        f"- 预测期: {payload.get('forecast_years', 'N/A')} 年",
        "- 基期: "
        f"{'LTM' if payload.get('ltm_baseline_enabled') else '最新年报'}",
        f"- 终值法: {payload.get('terminal_value_method', 'N/A')}",
    ]

    if payload.get("terminal_value_method") == "perpetual_growth":
        lines.append(
            f"- 永续增长率: {_format_percent(payload.get('perpetual_growth_rate'))}"
        )
    if payload.get("terminal_value_method") == "exit_multiple":
        exit_multiple = payload.get("exit_multiple")
        if exit_multiple is not None:
            lines.append(f"- 退出乘数: {exit_multiple}")

    wacc_overrides = _format_wacc_overrides(payload)
    lines.append(f"- WACC 覆盖: {wacc_overrides}")
    lines.append(
        f"- LLM 总结: {'开启' if payload.get('request_llm_summary') else '关闭'}"
    )

    if sensitivity:
        lines.append(
            "- 敏感性分析: "
            f"{row_axis.get('parameter_name')} x {column_axis.get('parameter_name')} "
            f"({len(row_axis.get('values', []))} x {len(column_axis.get('values', []))})"
        )
    else:
        lines.append("- 敏感性分析: 无")

    if changed_fields:
        preview = ", ".join(changed_fields[:8])
        if len(changed_fields) > 8:
            preview += ", ..."
        lines.append(f"- 关键自定义字段: {preview}")

    return "\n".join(lines)


def _format_wacc_overrides(payload: dict[str, Any]) -> str:
    fields = []
    for key in [
        "beta",
        "risk_free_rate",
        "market_risk_premium",
        "cost_of_debt",
        "target_debt_ratio",
    ]:
        value = payload.get(key)
        if value is not None:
            if "rate" in key or "premium" in key or "ratio" in key:
                fields.append(f"{key}={_format_percent(value)}")
            else:
                fields.append(f"{key}={value}")
    return ", ".join(fields) if fields else "无"


def _collect_changed_paths(
    current: Any,
    default: Any,
    *,
    prefix: str = "",
) -> list[str]:
    if isinstance(current, dict) and isinstance(default, dict):
        changed = []
        for key, value in current.items():
            if key.startswith("_skill_"):
                continue
            next_prefix = f"{prefix}.{key}" if prefix else key
            changed.extend(
                _collect_changed_paths(
                    value,
                    default.get(key),
                    prefix=next_prefix,
                )
            )
        return changed

    if current != default:
        return [prefix] if prefix else []
    return []


def _format_percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.2f}%"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
