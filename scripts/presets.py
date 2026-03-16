#!/usr/bin/env python3
"""Preset definitions and alias resolution for wenwengu-cli skill flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Preset:
    name: str
    description: str
    aliases: tuple[str, ...]
    payload: dict[str, Any]


VALUATION_PRESETS = {
    "base": Preset(
        name="base",
        description="Baseline request with a standard five-year horizon and the default exit-multiple DCF path.",
        aliases=("base", "baseline", "默认", "基准", "基础", "标准"),
        payload={
            "forecast_years": 5,
            "terminal_value_method": "exit_multiple",
        },
    ),
    "bull": Preset(
        name="bull",
        description="Bullish case with perpetual-growth terminal value and a slightly lower beta.",
        aliases=("bull", "optimistic", "乐观", "看多", "牛市"),
        payload={
            "forecast_years": 5,
            "terminal_value_method": "perpetual_growth",
            "perpetual_growth_rate": 0.03,
            "beta": 0.95,
        },
    ),
    "bear": Preset(
        name="bear",
        description="Bearish case with a tighter exit multiple and slightly higher beta.",
        aliases=("bear", "pessimistic", "悲观", "看空", "熊市"),
        payload={
            "forecast_years": 5,
            "terminal_value_method": "exit_multiple",
            "exit_multiple": 6.0,
            "beta": 1.15,
        },
    ),
    "conservative": Preset(
        name="conservative",
        description="Conservative case with perpetual growth capped near long-run nominal GDP.",
        aliases=("conservative", "谨慎", "保守", "稳健"),
        payload={
            "forecast_years": 5,
            "terminal_value_method": "perpetual_growth",
            "perpetual_growth_rate": 0.02,
            "beta": 1.10,
        },
    ),
    "high-growth": Preset(
        name="high-growth",
        description="Longer explicit forecast window for companies still in a strong growth phase.",
        aliases=("high-growth", "high growth", "growth", "高增长", "成长"),
        payload={
            "forecast_years": 7,
            "terminal_value_method": "perpetual_growth",
            "perpetual_growth_rate": 0.03,
        },
    ),
    "mature-stable": Preset(
        name="mature-stable",
        description="Mature and stable case with a lower perpetual growth anchor.",
        aliases=("mature-stable", "mature", "stable", "成熟", "成熟稳定", "稳定"),
        payload={
            "forecast_years": 5,
            "terminal_value_method": "perpetual_growth",
            "perpetual_growth_rate": 0.02,
            "mid_year_convention": True,
        },
    ),
}


SENSITIVITY_PRESETS = {
    "wacc-exit-standard": Preset(
        name="wacc-exit-standard",
        description="Standard 5x5 grid with WACC on rows and exit multiple on columns.",
        aliases=(
            "wacc-exit-standard",
            "exit-standard",
            "标准退出敏感性",
            "标准wacc退出",
        ),
        payload={
            "row_axis": {
                "parameter_name": "wacc",
                "values": [0.07, 0.08, 0.09, 0.10, 0.11],
            },
            "column_axis": {
                "parameter_name": "exit_multiple",
                "values": [6.0, 7.0, 8.0, 9.0, 10.0],
            },
        },
    ),
    "wacc-pgr-standard": Preset(
        name="wacc-pgr-standard",
        description="Standard 5x5 grid with WACC on rows and perpetual growth on columns.",
        aliases=(
            "wacc-pgr-standard",
            "pgr-standard",
            "标准永续增长敏感性",
            "标准wacc永续增长",
        ),
        payload={
            "row_axis": {
                "parameter_name": "wacc",
                "values": [0.07, 0.08, 0.09, 0.10, 0.11],
            },
            "column_axis": {
                "parameter_name": "perpetual_growth_rate",
                "values": [0.02, 0.025, 0.03, 0.035, 0.04],
            },
        },
    ),
    "wacc-exit-wide": Preset(
        name="wacc-exit-wide",
        description="Wide 7x7 grid with WACC and exit multiple ranges expanded.",
        aliases=("wacc-exit-wide", "wide-exit", "宽退出敏感性", "宽wacc退出"),
        payload={
            "row_axis": {
                "parameter_name": "wacc",
                "values": [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            },
            "column_axis": {
                "parameter_name": "exit_multiple",
                "values": [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
            },
        },
    ),
    "wacc-pgr-wide": Preset(
        name="wacc-pgr-wide",
        description="Wide 7x7 grid with WACC and perpetual growth ranges expanded.",
        aliases=("wacc-pgr-wide", "wide-pgr", "宽永续增长敏感性", "宽wacc永续增长"),
        payload={
            "row_axis": {
                "parameter_name": "wacc",
                "values": [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            },
            "column_axis": {
                "parameter_name": "perpetual_growth_rate",
                "values": [0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04],
            },
        },
    ),
}


def normalize_preset_name(raw_name: str) -> str:
    return raw_name.strip().lower().replace("_", "-")


def resolve_valuation_preset(raw_name: str) -> Preset:
    normalized = normalize_preset_name(raw_name)
    for preset in VALUATION_PRESETS.values():
        if normalized == preset.name:
            return preset
        if normalized in {normalize_preset_name(alias) for alias in preset.aliases}:
            return preset
    raise SystemExit(f"Unknown valuation preset: {raw_name}")


def resolve_sensitivity_preset(raw_name: str) -> Preset:
    normalized = normalize_preset_name(raw_name)
    for preset in SENSITIVITY_PRESETS.values():
        if normalized == preset.name:
            return preset
        if normalized in {normalize_preset_name(alias) for alias in preset.aliases}:
            return preset
    raise SystemExit(f"Unknown sensitivity preset: {raw_name}")


def format_preset_listing() -> str:
    lines = ["Valuation presets:"]
    for preset in VALUATION_PRESETS.values():
        lines.append(f"- {preset.name}: {preset.description}")
        lines.append(f"  aliases: {', '.join(preset.aliases)}")

    lines.append("")
    lines.append("Sensitivity presets:")
    for preset in SENSITIVITY_PRESETS.values():
        lines.append(f"- {preset.name}: {preset.description}")
        lines.append(f"  aliases: {', '.join(preset.aliases)}")

    return "\n".join(lines)
