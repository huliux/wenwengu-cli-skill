#!/usr/bin/env python3
"""Upgrade the packaged wenwengu valuation engine."""

from __future__ import annotations

import argparse
import sys

from binary_manager import DEFAULT_REPO_SLUG, detect_preferred_layout, install_binary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="upgrade_engine.py",
        description="Upgrade the packaged wenwengu valuation engine.",
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Release tag to install. Default: latest.",
    )
    parser.add_argument(
        "--release-source",
        default=DEFAULT_REPO_SLUG,
        help="GitHub release source used for engine downloads.",
    )
    parser.add_argument(
        "--layout",
        choices=["openclaw", "codex"],
        help="Install layout. Default: auto-detect from current runtime.",
    )
    parser.add_argument(
        "--archive-file",
        help="Upgrade from a local package file instead of downloading from GitHub.",
    )
    parser.add_argument(
        "--asset-url",
        help="Override the engine download URL.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    layout = args.layout or detect_preferred_layout()

    result = install_binary(
        version=args.version,
        repo_slug=args.release_source,
        layout=layout,
        archive_file=args.archive_file,
        asset_url=args.asset_url,
        force=True,
    )

    print("估值引擎升级完成")
    print(f"- 路径: {result['binary_path']}")
    print(f"- 布局: {result['layout']}")
    print(f"- 平台包: {result['asset_name']}")
    print(f"- 来源: {result['source_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
