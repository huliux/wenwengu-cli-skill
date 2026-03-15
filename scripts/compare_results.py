#!/usr/bin/env python3
"""Compare two valuation JSON payloads and summarize the delta."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import parse_json_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="compare_results.py",
        description="Compare two wenwengu valuation result payloads.",
    )
    parser.add_argument("--left", required=True, help="Left result JSON file.")
    parser.add_argument("--right", required=True, help="Right result JSON file.")
    parser.add_argument("--left-label", default="left", help="Left result label.")
    parser.add_argument("--right-label", default="right", help="Right result label.")

    args = parser.parse_args(argv)
    left_payload = _load_json_file(args.left)
    right_payload = _load_json_file(args.right)

    print(
        summarize_result_comparison(
            left_payload,
            right_payload,
            left_label=args.left_label,
            right_label=args.right_label,
        )
    )
    return 0


def summarize_result_comparison(
    left_payload: dict[str, Any],
    right_payload: dict[str, Any],
    *,
    left_label: str,
    right_label: str,
) -> str:
    left_core = _extract_core_metrics(left_payload)
    right_core = _extract_core_metrics(right_payload)
    value_change = _format_relative_change(
        left_core["value_per_share"],
        right_core["value_per_share"],
    )
    conclusion = (
        f"{right_label} 的每股价值相对 {left_label} 变化 {value_change}。"
        if value_change != "N/A"
        else f"{left_label} 与 {right_label} 的每股价值差异无法从结果中稳定判断。"
    )
    lines = [
        "结果对比",
        f"- 结论: {conclusion}",
        f"- 左侧: {left_label}",
        f"- 右侧: {right_label}",
    ]
    lines.extend(build_comparison_lines(left_payload, right_payload))
    return "\n".join(lines)


def build_comparison_lines(
    left_payload: dict[str, Any],
    right_payload: dict[str, Any],
) -> list[str]:
    left_core = _extract_core_metrics(left_payload)
    right_core = _extract_core_metrics(right_payload)

    lines = [
        f"- 标的: {left_core['name']} ({left_core['ts_code']})",
        "- 每股价值: "
        f"{_format_number(left_core['value_per_share'])} -> "
        f"{_format_number(right_core['value_per_share'])} "
        f"({_format_relative_change(left_core['value_per_share'], right_core['value_per_share'])})",
        "- WACC: "
        f"{_format_percent(left_core['wacc'])} -> "
        f"{_format_percent(right_core['wacc'])}",
        "- 终值法: "
        f"{left_core['terminal_method']} -> {right_core['terminal_method']}",
        "- 预测期: "
        f"{left_core['forecast_years']} -> {right_core['forecast_years']} 年",
        "- 数据警告数: "
        f"{left_core['warning_count']} -> {right_core['warning_count']}",
    ]

    if left_core["latest_price"] == right_core["latest_price"]:
        lines.append(f"- 现价: {_format_number(left_core['latest_price'])}")
    else:
        lines.append(
            "- 现价: "
            f"{_format_number(left_core['latest_price'])} -> "
            f"{_format_number(right_core['latest_price'])}"
        )

    return lines


def _extract_core_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    stock_info = payload.get("stock_info") or {}
    valuation_results = payload.get("valuation_results") or {}
    dcf_details = valuation_results.get("dcf_forecast_details") or {}
    warnings = valuation_results.get("data_warnings") or []

    return {
        "ts_code": stock_info.get("ts_code", "N/A"),
        "name": stock_info.get("name", "N/A"),
        "latest_price": valuation_results.get("latest_price"),
        "value_per_share": dcf_details.get("value_per_share"),
        "wacc": dcf_details.get("wacc_used"),
        "terminal_method": dcf_details.get("terminal_value_method_used", "N/A"),
        "forecast_years": dcf_details.get("forecast_period_years", "N/A"),
        "warning_count": len(warnings),
    }


def _format_relative_change(left_value: Any, right_value: Any) -> str:
    if left_value in (None, 0) or right_value is None:
        return "N/A"
    change = (float(right_value) / float(left_value)) - 1
    sign = "+" if change >= 0 else "-"
    return f"{sign}{abs(change) * 100:.2f}%"


def _format_percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def _format_number(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):,.2f}"


def _load_json_file(path: str) -> dict[str, Any]:
    return parse_json_payload(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
