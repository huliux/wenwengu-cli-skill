#!/usr/bin/env python3
"""Deterministic summaries for wenwengu-cli JSON payloads."""

from __future__ import annotations

from typing import Any


def summarize_payload(payload: dict[str, Any], *, kind: str = "auto") -> str:
    resolved_kind = detect_payload_kind(payload) if kind == "auto" else kind

    if resolved_kind == "valuation":
        return summarize_valuation(payload)
    if resolved_kind == "doctor":
        return summarize_doctor(payload)
    if resolved_kind == "screen":
        return summarize_screen(payload)
    if resolved_kind == "data":
        return summarize_data(payload)
    raise SystemExit(f"Unsupported summary kind: {resolved_kind}")


def detect_payload_kind(payload: dict[str, Any]) -> str:
    if "stock_info" in payload and "valuation_results" in payload:
        return "valuation"
    if "overall_status" in payload and "checks" in payload:
        return "doctor"
    if "records" in payload and "filters" in payload:
        return "screen"
    if "action" in payload and "status" in payload:
        return "data"
    raise SystemExit("Unable to detect payload kind from JSON.")


def summarize_valuation(payload: dict[str, Any]) -> str:
    stock_info = payload.get("stock_info") or {}
    valuation_results = payload.get("valuation_results") or {}
    dcf_details = valuation_results.get("dcf_forecast_details") or {}
    warnings = valuation_results.get("data_warnings") or []

    latest_price = valuation_results.get("latest_price")
    value_per_share = dcf_details.get("value_per_share")
    premium_discount = _format_premium_discount(value_per_share, latest_price)

    conclusion = premium_discount or "已完成估值，但缺少足够数据判断相对现价高低。"
    warning_text = "；".join(str(item) for item in warnings[:3]) if warnings else "无"

    lines = [
        "估值摘要",
        f"- 结论: {conclusion}",
        f"- 标的: {stock_info.get('name', 'N/A')} ({stock_info.get('ts_code', 'N/A')})",
        f"- 每股价值: {_format_number(value_per_share)}",
        f"- 最新价格: {_format_number(latest_price)}",
        "- 核心参数: "
        f"WACC {_format_percent(dcf_details.get('wacc_used'))} | "
        f"终值法 {dcf_details.get('terminal_value_method_used', 'N/A')} | "
        f"预测期 {dcf_details.get('forecast_period_years', 'N/A')} 年",
        f"- 风险提示: {warning_text}",
    ]

    return "\n".join(lines)


def summarize_doctor(payload: dict[str, Any]) -> str:
    failed_checks = [
        check for check in payload.get("checks", []) if check.get("status") != "ok"
    ]
    conclusion = (
        "当前环境可以继续执行本地 CLI 流程。"
        if not failed_checks
        else "当前环境存在阻塞项，建议先修复后再执行估值或筛选。"
    )
    lines = [
        "环境诊断",
        f"- 结论: {conclusion}",
        f"- 总体状态: {payload.get('overall_status', 'unknown')}",
        f"- 数据源: {payload.get('data_source', 'unknown')}",
    ]

    if not failed_checks:
        lines.append("- 失败项: 无")
        return "\n".join(lines)

    failed_text = "；".join(
        f"{check.get('name')}: {check.get('message')}" for check in failed_checks
    )
    lines.append(f"- 失败项: {failed_text}")
    return "\n".join(lines)


def summarize_screen(payload: dict[str, Any]) -> str:
    records = payload.get("records") or []
    filters = payload.get("filters") or {}
    preview_text = (
        "；".join(
            f"{record.get('ts_code')} {record.get('name')} | "
            f"PE {_format_number(record.get('pe'))} | "
            f"PB {_format_number(record.get('pb'))} | "
            f"市值 {_format_number(record.get('market_cap_billion'))} B"
            for record in records[:3]
        )
        if records
        else "无"
    )

    lines = [
        "筛选摘要",
        f"- 结论: 命中 {payload.get('count', len(records))} 条记录。",
        f"- 交易日: {payload.get('trade_date', 'N/A')}",
        f"- 结果数: {payload.get('count', len(records))}",
        f"- 过滤条件: {_format_filters(filters)}",
        f"- 结果预览: {preview_text}",
    ]
    return "\n".join(lines)


def summarize_data(payload: dict[str, Any]) -> str:
    action = payload.get("action", "unknown")
    status = payload.get("status", "unknown")
    conclusion = (
        "这是只读状态检查。"
        if action == "status"
        else "数据刷新命令已执行。"
    )
    lines = [
        "数据摘要",
        f"- 结论: {conclusion}",
        f"- 动作: {action}",
        f"- 状态: {status}",
    ]

    if action == "status":
        cache_stats = payload.get("cache_stats") or {}
        lines.extend(
            [
                f"- 最新交易日: {payload.get('latest_trade_date', 'N/A')}",
                "- 缓存: "
                f"{cache_stats.get('current_total_files', 'N/A')} files, "
                f"{_format_number(cache_stats.get('current_total_size_mb'))} MB, "
                f"hit rate {_format_number(cache_stats.get('hit_rate'))}%",
            ]
        )
        return "\n".join(lines)

    if "trade_date" in payload:
        lines.append(f"- 交易日: {payload.get('trade_date')}")
    if "count" in payload:
        lines.append(f"- 记录数: {payload.get('count')}")
    return "\n".join(lines)


def _format_filters(filters: dict[str, Any]) -> str:
    active_filters = [
        f"{key}={value}"
        for key, value in filters.items()
        if value is not None and value != ""
    ]
    return ", ".join(active_filters) if active_filters else "无"


def _format_premium_discount(value_per_share: Any, latest_price: Any) -> str | None:
    if value_per_share in (None, 0) or latest_price in (None, 0):
        return None

    ratio = (float(value_per_share) / float(latest_price)) - 1
    relation = "高于现价" if ratio >= 0 else "低于现价"
    return f"DCF 每股价值 {relation} {abs(ratio) * 100:.2f}%"


def _format_percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def _format_number(value: Any) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)
