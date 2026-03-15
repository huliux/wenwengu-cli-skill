#!/usr/bin/env python3
"""Locate the wenwengu repository and forward commands to wenwengu-cli."""

from __future__ import annotations

import argparse
import sys

from _common import normalize_cli_args, run_wenwengu_cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_cli.py",
        description="Run wenwengu-cli from a detected repo path or packaged binary.",
    )
    parser.add_argument(
        "--repo",
        help="Explicit repository root. Defaults to WENWENGU_CLI_REPO or the nearest parent wenwengu repo.",
    )
    parser.add_argument(
        "--bin",
        help="Explicit wenwengu-cli binary path. Defaults to WENWENGU_CLI_BIN when set.",
    )

    args, raw_cli_args = parser.parse_known_args(argv)
    cli_args = normalize_cli_args(raw_cli_args)
    if not cli_args:
        parser.error(
            "Provide a wenwengu-cli subcommand, for example: doctor --output json"
        )

    return run_wenwengu_cli(
        cli_args,
        explicit_repo=args.repo,
        explicit_bin=args.bin,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
