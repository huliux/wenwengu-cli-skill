#!/usr/bin/env python3
"""Check whether the packaged wenwengu-cli binary is discoverable and runnable."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from binary_manager import find_installed_binary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_binary.py",
        description="Check whether the packaged wenwengu-cli binary is installed.",
    )
    parser.add_argument("--bin", help="Explicit binary path override.")
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

    candidate = find_installed_binary(explicit_path=args.bin)
    payload: dict[str, object] = {
        "found": False,
        "path": None,
        "source": None,
        "runnable": False,
        "returncode": None,
        "stderr": "",
    }

    if candidate is not None:
        payload["found"] = True
        payload["path"] = str(candidate.path)
        payload["source"] = candidate.source
        completed = subprocess.run(
            [str(candidate.path), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        payload["runnable"] = completed.returncode == 0
        payload["returncode"] = completed.returncode
        payload["stderr"] = completed.stderr.strip()

    if args.output == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if not payload["found"]:
            print("未发现 wenwengu-cli 二进制。")
        else:
            print("二进制检查")
            print(f"- 来源: {payload['source']}")
            print(f"- 路径: {payload['path']}")
            print(
                "- 可执行: "
                f"{'是' if payload['runnable'] else '否'}"
            )
            if payload["stderr"]:
                print(f"- 错误: {payload['stderr']}")

    return 0 if payload["found"] and payload["runnable"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
