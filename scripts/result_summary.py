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
    raise SystemExit(f"Unsupported summary kind: {resolved_kind}")


def detect_payload_kind(payload: dict[str, Any]) -> str:
    if "stock_info" in payload and "valuation_results" in payload:
        return "valuation"
    if "overall_status" in payload and "checks" in payload:
        return "doctor"
    raise SystemExit("Unable to detect payload kind from JSON.")


def summarize_valuation(payload: dict[str, Any]) -> str:
    error_text = str(payload.get("error") or "").strip()
    if error_text:
        lines = [
            "估值摘要",
            f"- 结论: 估值执行失败：{error_text}",
        ]
        if "股票代码匹配" in error_text:
            lines.extend(
                [
                    "- 建议修复: 检查 DATA_SOURCE 与数据库或 Tushare 配置是否匹配，然后升级到最新估值引擎。",
                    "- 命令: openclaw gateway restart",
                    "- 命令: python scripts/upgrade_engine.py",
                ]
            )
        return "\n".join(lines)

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
    data_source = payload.get("data_source", "unknown")
    failed_checks = [
        check for check in payload.get("checks", []) if check.get("status") == "fail"
    ]
    warn_checks = [
        check for check in payload.get("checks", []) if check.get("status") == "warn"
    ]
    conclusion = (
        "当前环境可以继续执行本地 CLI 流程。"
        if not failed_checks
        else "当前环境存在阻塞项，建议先修复后再执行估值。"
    )
    lines = [
        "环境诊断",
        f"- 结论: {conclusion}",
        f"- 总体状态: {payload.get('overall_status', 'unknown')}",
        f"- 数据源: {data_source}",
    ]

    if warn_checks:
        warn_text = "；".join(
            f"{check.get('name')}: {check.get('message')}" for check in warn_checks
        )
        lines.append(f"- 提示项: {warn_text}")

    if not failed_checks:
        lines.append("- 失败项: 无")
        return "\n".join(lines)

    failed_text = "；".join(
        f"{check.get('name')}: {check.get('message')}" for check in failed_checks
    )
    lines.append(f"- 失败项: {failed_text}")
    has_tushare_fail = any(check.get("name") == "tushare" for check in failed_checks)
    has_postgres_fail = any(check.get("name") == "postgres" for check in failed_checks)
    if has_postgres_fail or data_source == "postgres":
        lines.extend(
            [
                "- 建议修复: 为 skill 配置数据库连接串或 DB_* 环境变量后重试。",
                '- 命令: openclaw config set skills.entries.wenwengu-cli.primaryEnv "DATABASE_URL"',
                '- 命令: openclaw config set skills.entries.wenwengu-cli.env.DATABASE_URL "postgresql://user:password@host:5432/dbname"',
                '- 命令: openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "postgres"',
                "- 命令: openclaw gateway restart",
            ]
        )
    elif has_tushare_fail:
        lines.extend(
            [
                "- 建议修复: 在 OpenClaw 配置 TUSHARE token 后重试。",
                '- 命令: openclaw config set skills.entries.wenwengu-cli.apiKey "your_tushare_token"',
                '- 命令: openclaw config set skills.entries.wenwengu-cli.primaryEnv "TUSHARE_TOKEN"',
                '- 命令: openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "tushare"',
                "- 命令: openclaw gateway restart",
            ]
        )
    return "\n".join(lines)


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
