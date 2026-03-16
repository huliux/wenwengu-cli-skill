#!/usr/bin/env python3
"""Check whether the packaged wenwengu valuation engine is discoverable and runnable."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from binary_manager import find_installed_binary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_engine.py",
        description="Check whether the packaged wenwengu valuation engine is installed.",
    )
    parser.add_argument("--bin", help="Explicit valuation engine path override.")
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output mode. Default: text.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    explicit_path = Path(args.bin).expanduser().resolve() if args.bin else None
    candidate_path: Path | None = None
    candidate_source: str | None = None
    if explicit_path is not None:
        if explicit_path.exists():
            candidate_path = explicit_path
            candidate_source = "explicit"
    else:
        candidate = find_installed_binary()
        if candidate is not None:
            candidate_path = candidate.path
            candidate_source = candidate.source

    payload: dict[str, object] = {
        "found": False,
        "path": None,
        "source": None,
        "runnable": False,
        "returncode": None,
        "stderr": "",
    }

    if candidate_path is not None:
        payload["found"] = True
        payload["path"] = str(candidate_path)
        payload["source"] = candidate_source
        completed = subprocess.run(
            [str(candidate_path), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        payload["runnable"] = completed.returncode == 0
        payload["returncode"] = completed.returncode
        payload["stderr"] = completed.stderr.strip()
    elif explicit_path is not None:
        payload["source"] = "explicit"
        payload["path"] = str(explicit_path)
        payload["stderr"] = (
            f"Configured wenwengu valuation engine was not found: {explicit_path}"
        )

    if args.output == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if not payload["found"]:
            print("未发现 wenwengu 估值引擎。")
            if payload["stderr"]:
                print(f"- 错误: {payload['stderr']}")
        else:
            print("估值引擎检查")
            print(f"- 来源: {payload['source']}")
            print(f"- 路径: {payload['path']}")
            print(f"- 可执行: {'是' if payload['runnable'] else '否'}")
            if payload["stderr"]:
                print(f"- 错误: {payload['stderr']}")

    return 0 if payload["found"] and payload["runnable"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
