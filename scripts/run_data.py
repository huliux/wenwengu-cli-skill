#!/usr/bin/env python3
"""Run `wenwengu-cli data` with skill-friendly defaults."""

from __future__ import annotations

import argparse
import sys

from _common import normalize_cli_args, run_with_optional_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_data.py",
        description="Run wenwengu-cli data using repo or binary resolution.",
    )
    parser.add_argument("--repo", help="Explicit repository root.")
    parser.add_argument("--bin", help="Explicit wenwengu-cli binary path.")
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Print a concise summary instead of raw JSON output.",
    )

    args, raw_cli_args = parser.parse_known_args(argv)
    cli_args = normalize_cli_args(raw_cli_args)

    if not cli_args:
        parser.error(
            "Provide a data subcommand such as status, update-stock-basic, "
            "or update-daily-basic."
        )

    return run_with_optional_summary(
        "data",
        cli_args,
        expected_kind="data",
        summarize=args.summarize,
        explicit_repo=args.repo,
        explicit_bin=args.bin,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
