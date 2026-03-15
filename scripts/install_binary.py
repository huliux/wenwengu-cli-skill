#!/usr/bin/env python3
"""Install the packaged wenwengu-cli binary for OpenClaw or Codex use."""

from __future__ import annotations

import argparse
import sys

from binary_manager import install_binary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install_binary.py",
        description="Install the packaged wenwengu-cli binary.",
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Release tag to install. Default: latest.",
    )
    parser.add_argument(
        "--repo-slug",
        default="huliux/wenwengu-cli-skill",
        help="GitHub repo slug used for release downloads.",
    )
    parser.add_argument(
        "--layout",
        choices=["openclaw", "codex"],
        default="openclaw",
        help="Install layout. Default: openclaw.",
    )
    parser.add_argument(
        "--archive-file",
        help="Install from a local archive file instead of downloading from GitHub.",
    )
    parser.add_argument(
        "--asset-url",
        help="Override the binary download URL.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace any existing installed binary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = install_binary(
        version=args.version,
        repo_slug=args.repo_slug,
        layout=args.layout,
        archive_file=args.archive_file,
        asset_url=args.asset_url,
        force=args.force,
    )

    print("二进制安装完成")
    print(f"- 路径: {result['binary_path']}")
    print(f"- 布局: {result['layout']}")
    print(f"- 平台包: {result['asset_name']}")
    print(f"- 来源: {result['source_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
