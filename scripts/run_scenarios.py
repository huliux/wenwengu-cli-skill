#!/usr/bin/env python3
"""Run multiple scenario presets and summarize the comparison."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import capture_wenwengu_cli, create_temp_request_file, parse_json_payload
from compare_results import build_comparison_lines
from presets import resolve_valuation_preset


SCRIPT_DIR = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_scenarios.py",
        description="Run multiple valuation scenario presets and summarize the result.",
    )
    parser.add_argument("--repo", help="Explicit repository root.")
    parser.add_argument("--bin", help="Explicit wenwengu-cli binary path.")
    parser.add_argument("--ts-code", help="Stock code, for example 600519.SH.")
    parser.add_argument(
        "--base-request",
        help="Optional base request.json merged under every scenario preset.",
    )
    parser.add_argument(
        "--scenarios",
        default="base,bull,bear",
        help="Comma-separated valuation preset names. Default: base,bull,bear.",
    )
    parser.add_argument("--valuation-date", help="Valuation date in YYYY-MM-DD.")
    parser.add_argument("--forecast-years", type=int, help="Forecast years override.")
    parser.add_argument(
        "--sensitivity-preset",
        help="Optional sensitivity preset applied to each scenario.",
    )
    parser.add_argument("--llm-summary", action="store_true", help="Request LLM summary.")
    parser.add_argument("--ltm-baseline", action="store_true", help="Enable LTM baseline.")
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Additional KEY=VALUE override applied to every scenario.",
    )
    parser.add_argument(
        "--output",
        choices=["summary", "json"],
        default="summary",
        help="Output mode. Default: summary.",
    )

    args = parser.parse_args(argv)

    scenario_names = [item.strip() for item in args.scenarios.split(",") if item.strip()]
    if not scenario_names:
        parser.error("Provide at least one scenario preset.")

    results = []
    for scenario_name in scenario_names:
        preset = resolve_valuation_preset(scenario_name)
        request_payload = _make_request_payload(args, preset.name)
        request_file = create_temp_request_file(request_payload)

        completed = capture_wenwengu_cli(
            ["valuate", "--request-file", str(request_file), "--output", "json"],
            explicit_repo=args.repo,
            explicit_bin=args.bin,
        )
        if completed.returncode != 0:
            if completed.stderr:
                sys.stderr.write(completed.stderr)
            if completed.stdout:
                sys.stdout.write(completed.stdout)
            return completed.returncode

        results.append(
            {
                "scenario": preset.name,
                "request": request_payload,
                "result": parse_json_payload(completed.stdout),
            }
        )

    if args.output == "json":
        import json

        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    print(summarize_scenario_matrix(results))
    return 0


def summarize_scenario_matrix(results: list[dict]) -> str:
    first_result = results[0]["result"]
    stock_info = first_result.get("stock_info") or {}
    ranked = sorted(
        results,
        key=lambda item: _safe_float(
            (
                (
                    (item["result"].get("valuation_results") or {}).get(
                        "dcf_forecast_details"
                    )
                    or {}
                ).get("value_per_share")
            )
        ),
        reverse=True,
    )
    highest = ranked[0]["scenario"]
    lowest = ranked[-1]["scenario"]
    lines = [
        "情景矩阵",
        f"- 结论: {highest} 情景的每股价值最高，{lowest} 情景最低。",
        f"- 标的: {stock_info.get('name', 'N/A')} ({stock_info.get('ts_code', 'N/A')})",
        f"- 情景数: {len(results)}",
        "- 各情景结果:",
    ]

    for item in results:
        dcf = ((item["result"].get("valuation_results") or {}).get("dcf_forecast_details") or {})
        lines.append(
            "  - "
            f"{item['scenario']}: 每股价值 {_format_number(dcf.get('value_per_share'))} | "
            f"WACC {_format_percent(dcf.get('wacc_used'))} | "
            f"终值法 {dcf.get('terminal_value_method_used')}"
        )

    baseline = results[0]
    if len(results) > 1:
        lines.append("- 与首个情景对比:")
        for item in results[1:]:
            comparison_lines = build_comparison_lines(baseline["result"], item["result"])
            lines.append(f"  - {item['scenario']} vs {baseline['scenario']}:")
            for comparison_line in comparison_lines[1:]:
                lines.append(f"    {comparison_line}")

    return "\n".join(lines)


def _safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")


def _format_number(value) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def _format_percent(value) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def _make_request_payload(args, scenario_name: str) -> dict:
    import subprocess

    command = [
        sys.executable,
        str(SCRIPT_DIR / "make_request.py"),
        "--stdout",
        "--no-validate",
        "--preset",
        scenario_name,
    ]

    if args.repo:
        command.extend(["--repo", args.repo])
    if args.base_request:
        command.extend(["--base-request", args.base_request])
    if args.ts_code:
        command.extend(["--ts-code", args.ts_code])
    if args.valuation_date:
        command.extend(["--valuation-date", args.valuation_date])
    if args.forecast_years is not None:
        command.extend(["--forecast-years", str(args.forecast_years)])
    if args.sensitivity_preset:
        command.extend(["--sensitivity-preset", args.sensitivity_preset])
    if args.llm_summary:
        command.append("--llm-summary")
    if args.ltm_baseline:
        command.append("--ltm-baseline")
    command.extend(["--label", scenario_name])
    for override in args.overrides:
        command.extend(["--set", override])

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        error_output = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(error_output)
    return parse_json_payload(completed.stdout)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
