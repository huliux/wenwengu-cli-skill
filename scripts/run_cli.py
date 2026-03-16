#!/usr/bin/env python3
"""Locate the wenwengu valuation engine and forward commands."""

from __future__ import annotations

import argparse
import sys

from _common import normalize_cli_args, run_wenwengu_cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_cli.py",
        description="Run wenwengu-cli from an installed valuation engine.",
    )
    parser.add_argument(
        "--bin",
        help="Explicit valuation engine path. Defaults to WENWENGU_CLI_BIN when set.",
    )

    args, raw_cli_args = parser.parse_known_args(argv)
    cli_args = normalize_cli_args(raw_cli_args)
    if not cli_args:
        parser.error(
            "Provide a wenwengu-cli subcommand, for example: doctor --output json"
        )

    return run_wenwengu_cli(
        cli_args,
        explicit_bin=args.bin,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
