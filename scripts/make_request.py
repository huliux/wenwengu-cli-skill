#!/usr/bin/env python3
"""Generate a reproducible request.json for complex wenwengu valuation runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import (
    create_temp_request_file,
    parse_json_payload,
    parse_override_value,
    set_nested_value,
    split_override,
)
from presets import (
    format_preset_listing,
    resolve_sensitivity_preset,
    resolve_valuation_preset,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="make_request.py",
        description="Generate a request.json for wenwengu-cli valuate.",
    )
    parser.add_argument(
        "--base-request",
        help="Load an existing request.json first, then merge preset and flag overrides on top.",
    )
    parser.add_argument(
        "--preset",
        help="Apply a valuation preset such as base, bull, bear, conservative, high-growth, or mature-stable.",
    )
    parser.add_argument(
        "--sensitivity-preset",
        help="Apply a sensitivity preset such as wacc-exit-standard or wacc-pgr-standard.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List supported valuation and sensitivity presets, then exit.",
    )
    parser.add_argument("--ts-code", help="Stock code, for example 600519.SH.")
    parser.add_argument("--label", help="Optional scenario label for downstream workflows.")
    parser.add_argument("--valuation-date", help="Valuation date in YYYY-MM-DD.")
    parser.add_argument("--forecast-years", type=int, help="Forecast years.")
    parser.add_argument(
        "--llm-summary",
        action="store_true",
        help="Set request_llm_summary=true.",
    )
    parser.add_argument(
        "--ltm-baseline",
        action="store_true",
        help="Set ltm_baseline_enabled=true.",
    )
    parser.add_argument(
        "--terminal-value-method",
        choices=["exit_multiple", "perpetual_growth"],
        help="Terminal value method.",
    )
    parser.add_argument("--exit-multiple", type=float, help="Exit multiple.")
    parser.add_argument(
        "--perpetual-growth-rate",
        type=float,
        help="Perpetual growth rate.",
    )
    parser.add_argument("--beta", type=float, help="Beta override.")
    parser.add_argument("--risk-free-rate", type=float, help="Risk-free rate override.")
    parser.add_argument(
        "--market-risk-premium",
        type=float,
        help="Market risk premium override.",
    )
    parser.add_argument("--cost-of-debt", type=float, help="Cost of debt override.")
    parser.add_argument("--target-debt-ratio", type=float, help="Target debt ratio override.")
    parser.add_argument(
        "--wacc-weight-mode",
        choices=["target", "market"],
        help="WACC weight mode.",
    )
    parser.add_argument(
        "--mid-year-convention",
        action="store_true",
        help="Enable mid-year convention.",
    )
    parser.add_argument(
        "--sensitivity-row-parameter",
        help="Override sensitivity row parameter name.",
    )
    parser.add_argument(
        "--sensitivity-row-values",
        help="JSON list for sensitivity row values, for example '[0.08, 0.09, 0.10]'.",
    )
    parser.add_argument(
        "--sensitivity-column-parameter",
        help="Override sensitivity column parameter name.",
    )
    parser.add_argument(
        "--sensitivity-column-values",
        help="JSON list for sensitivity column values.",
    )
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Additional KEY=VALUE override using dotted paths.",
    )
    parser.add_argument(
        "--output-file",
        help="Write the generated JSON to this path.",
    )
    parser.add_argument(
        "--temp-file",
        action="store_true",
        help="Write the generated JSON to a temporary file and print the path.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the generated JSON to stdout. This is the default if no file target is set.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_presets:
        print(format_preset_listing())
        return 0

    payload = build_payload(args)

    destination_count = sum(
        1 for enabled in [bool(args.output_file), args.temp_file, args.stdout] if enabled
    )
    if destination_count > 1:
        parser.error("Choose only one of --output-file, --temp-file, or --stdout.")

    if args.output_file:
        output_path = Path(args.output_file).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(output_path)
        return 0

    if args.temp_file:
        temp_path = create_temp_request_file(payload)
        print(temp_path)
        return 0

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_payload(args) -> dict:
    payload: dict = {}

    if args.base_request:
        payload.update(_load_request_file(args.base_request))

    if args.preset:
        payload = _deep_merge_dicts(payload, resolve_valuation_preset(args.preset).payload)

    if args.ts_code:
        payload["ts_code"] = args.ts_code
    if not payload.get("ts_code"):
        raise SystemExit("Provide --ts-code or include ts_code in --base-request.")
    if args.label:
        payload["_skill_scenario_label"] = args.label

    scalar_fields = {
        "valuation_date": args.valuation_date,
        "forecast_years": args.forecast_years,
        "terminal_value_method": args.terminal_value_method,
        "exit_multiple": args.exit_multiple,
        "perpetual_growth_rate": args.perpetual_growth_rate,
        "beta": args.beta,
        "risk_free_rate": args.risk_free_rate,
        "market_risk_premium": args.market_risk_premium,
        "cost_of_debt": args.cost_of_debt,
        "target_debt_ratio": args.target_debt_ratio,
        "wacc_weight_mode": args.wacc_weight_mode,
    }

    for key, value in scalar_fields.items():
        if value is not None:
            payload[key] = value

    if args.llm_summary:
        payload["request_llm_summary"] = True
    if args.ltm_baseline:
        payload["ltm_baseline_enabled"] = True
    if args.mid_year_convention:
        payload["mid_year_convention"] = True

    sensitivity = build_sensitivity_payload(args)
    if sensitivity is not None:
        payload["sensitivity_analysis"] = sensitivity

    for item in args.overrides:
        key, raw_value = split_override(item)
        set_nested_value(payload, key, parse_override_value(raw_value))

    return payload


def build_sensitivity_payload(args) -> dict | None:
    row_parameter = args.sensitivity_row_parameter
    row_values = parse_optional_json_list(args.sensitivity_row_values)
    column_parameter = args.sensitivity_column_parameter
    column_values = parse_optional_json_list(args.sensitivity_column_values)

    if args.sensitivity_preset:
        preset_payload = resolve_sensitivity_preset(args.sensitivity_preset).payload
        row_parameter = row_parameter or preset_payload["row_axis"]["parameter_name"]
        row_values = row_values or preset_payload["row_axis"]["values"]
        column_parameter = (
            column_parameter or preset_payload["column_axis"]["parameter_name"]
        )
        column_values = column_values or preset_payload["column_axis"]["values"]

    if not any([row_parameter, row_values, column_parameter, column_values]):
        return None

    if not all([row_parameter, row_values, column_parameter, column_values]):
        raise SystemExit(
            "Sensitivity configuration requires both row and column parameter/value pairs."
        )

    return {
        "row_axis": {
            "parameter_name": row_parameter,
            "values": row_values,
        },
        "column_axis": {
            "parameter_name": column_parameter,
            "values": column_values,
        },
    }


def parse_optional_json_list(raw_value: str | None) -> list[float] | None:
    if raw_value is None:
        return None

    parsed = parse_override_value(raw_value)
    if not isinstance(parsed, list):
        raise SystemExit(
            f"Expected a JSON list for sensitivity values, got: {raw_value}"
        )
    return parsed


def _load_request_file(request_file: str) -> dict:
    request_path = Path(request_file).expanduser().resolve()
    if not request_path.exists():
        raise SystemExit(f"Request file not found: {request_path}")
    return parse_json_payload(request_path.read_text(encoding="utf-8"))


def _deep_merge_dicts(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
