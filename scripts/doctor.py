#!/usr/bin/env python3
"""Run `wenwengu-cli doctor` with skill-friendly defaults."""

from __future__ import annotations

import argparse
import sys

from _common import normalize_cli_args, run_with_optional_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doctor.py",
        description="Run wenwengu-cli doctor using the installed valuation engine first.",
    )
    parser.add_argument("--bin", help="Explicit valuation engine path.")
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Print a concise summary instead of raw JSON output.",
    )

    args, raw_cli_args = parser.parse_known_args(argv)
    cli_args = normalize_cli_args(raw_cli_args)
    return run_with_optional_summary(
        "doctor",
        cli_args,
        expected_kind="doctor",
        summarize=args.summarize,
        explicit_bin=args.bin,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
