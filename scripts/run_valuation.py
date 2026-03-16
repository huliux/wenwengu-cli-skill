#!/usr/bin/env python3
"""Run `wenwengu-cli valuate` with skill-friendly defaults."""

from __future__ import annotations

import argparse
import sys

from _common import normalize_cli_args, run_with_optional_summary


def _has_option(args: list[str], option_name: str) -> bool:
    option_prefix = f"{option_name}="
    for index, arg in enumerate(args):
        if arg == option_name and index + 1 < len(args):
            value = args[index + 1].strip()
            if value and not value.startswith("-"):
                return True
        if arg.startswith(option_prefix):
            value = arg.split("=", 1)[1].strip()
            if value:
                return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_valuation.py",
        description="Run wenwengu-cli valuate using the installed valuation engine first.",
    )
    parser.add_argument("--bin", help="Explicit valuation engine path.")
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Print a concise summary instead of raw JSON output.",
    )

    args, raw_cli_args = parser.parse_known_args(argv)
    cli_args = normalize_cli_args(raw_cli_args)

    has_request_file = _has_option(cli_args, "--request-file")
    has_ts_code = _has_option(cli_args, "--ts-code")
    if not has_request_file and not has_ts_code:
        parser.error("Provide --ts-code or --request-file for valuation runs.")

    return run_with_optional_summary(
        "valuate",
        cli_args,
        expected_kind="valuation",
        summarize=args.summarize,
        explicit_bin=args.bin,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
