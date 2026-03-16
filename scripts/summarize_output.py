#!/usr/bin/env python3
"""Summarize wenwengu-cli JSON output from stdin or a file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from result_summary import summarize_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="summarize_output.py",
        description="Summarize a wenwengu-cli JSON payload.",
    )
    parser.add_argument(
        "--kind",
        choices=["auto", "valuation", "doctor"],
        default="auto",
        help="Payload kind. Defaults to auto-detect.",
    )
    parser.add_argument(
        "--input",
        help="Optional JSON file path. Defaults to reading from stdin.",
    )

    args = parser.parse_args(argv)
    raw_payload = _read_input(args.input)

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse JSON input: {exc}") from exc

    print(summarize_payload(payload, kind=args.kind))
    return 0


def _read_input(input_path: str | None) -> str:
    if input_path:
        return Path(input_path).read_text(encoding="utf-8")
    return sys.stdin.read()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
