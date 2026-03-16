#!/usr/bin/env python3
"""Shared helpers for wenwengu-cli skill wrappers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from binary_manager import detect_preferred_layout, find_installed_binary, install_binary
from result_summary import summarize_payload


def normalize_cli_args(raw_args: Sequence[str]) -> list[str]:
    args = list(raw_args)
    if args and args[0] == "--":
        return args[1:]
    return args


def ensure_output(cli_args: Sequence[str], default_output: str = "json") -> list[str]:
    args = list(cli_args)
    if get_output_mode(args) is not None:
        return args
    return [*args, "--output", default_output]


def ensure_json_output(cli_args: Sequence[str]) -> list[str]:
    args = list(cli_args)
    output_mode = get_output_mode(args)
    if output_mode is None:
        return [*args, "--output", "json"]
    if output_mode != "json":
        raise SystemExit("--summarize requires JSON output. Omit --output or use --output json.")
    return args


def get_output_mode(cli_args: Sequence[str]) -> str | None:
    args = list(cli_args)
    for index, arg in enumerate(args):
        if arg == "--output" and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith("--output="):
            return arg.split("=", 1)[1]
    return None


def resolve_binary(explicit_bin: str | None) -> Path | None:
    if explicit_bin:
        explicit_path = Path(explicit_bin).expanduser().resolve()
        if not explicit_path.exists():
            raise SystemExit(
                "Configured wenwengu valuation engine was not found: "
                f"{explicit_path}"
            )
        return explicit_path

    env_bin = os.getenv("WENWENGU_CLI_BIN")
    if env_bin:
        env_path = Path(env_bin).expanduser().resolve()
        if not env_path.exists():
            raise SystemExit(
                "Configured wenwengu valuation engine was not found: "
                f"{env_path}"
            )
        return env_path

    candidate = find_installed_binary()
    if candidate is None:
        return None
    return candidate.path


def run_wenwengu_cli(
    cli_args: Sequence[str],
    *,
    explicit_bin: str | None = None,
) -> int:
    command, cwd = build_wenwengu_command(
        cli_args,
        explicit_bin=explicit_bin,
    )
    completed = subprocess.run(command, cwd=cwd, check=False)
    return completed.returncode


def capture_wenwengu_cli(
    cli_args: Sequence[str],
    *,
    explicit_bin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command, cwd = build_wenwengu_command(
        cli_args,
        explicit_bin=explicit_bin,
    )
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def run_with_optional_summary(
    subcommand: str,
    cli_args: Sequence[str],
    *,
    expected_kind: str,
    summarize: bool,
    explicit_bin: str | None = None,
) -> int:
    if not summarize:
        return run_wenwengu_cli(
            [subcommand, *ensure_output(cli_args, default_output="json")],
            explicit_bin=explicit_bin,
        )

    completed = capture_wenwengu_cli(
        [subcommand, *ensure_json_output(cli_args)],
        explicit_bin=explicit_bin,
    )
    return emit_summary_from_completed(completed, expected_kind=expected_kind)


def emit_summary_from_completed(
    completed: subprocess.CompletedProcess[str],
    *,
    expected_kind: str,
) -> int:
    if completed.stderr:
        sys.stderr.write(completed.stderr)

    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        return completed.returncode

    payload = parse_json_payload(completed.stdout)
    print(summarize_payload(payload, kind=expected_kind))
    return 0


def parse_json_payload(raw_output: str):
    cleaned_output = raw_output.strip()
    if not cleaned_output:
        raise SystemExit("The CLI returned no JSON output to summarize.")

    try:
        return json.loads(cleaned_output)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse CLI JSON output: {exc}") from exc


def split_override(item: str) -> tuple[str, str]:
    if "=" not in item:
        raise SystemExit(f"Invalid override '{item}'. Expected KEY=VALUE.")
    key, value = item.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit(f"Invalid override '{item}'. Empty key.")
    return key, value.strip()


def parse_override_value(raw_value: str):
    lowered = raw_value.lower()
    if lowered in {"true", "false", "null"}:
        return json.loads(lowered)

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value


def set_nested_value(payload: dict, dotted_key: str, value) -> None:
    current = payload
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        existing = current.get(part)
        if not isinstance(existing, dict):
            existing = {}
            current[part] = existing
        current = existing
    current[parts[-1]] = value


def create_temp_request_file(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="wenwengu-request-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        return Path(handle.name)


def build_wenwengu_command(
    cli_args: Sequence[str],
    *,
    explicit_bin: str | None = None,
) -> tuple[list[str], Path]:
    binary_path = resolve_binary(explicit_bin)
    if binary_path is None:
        binary_path = auto_install_engine()

    cwd = Path.cwd()

    if binary_path is not None:
        command = [str(binary_path), *cli_args]
    else:
        raise SystemExit(
            "Unable to locate the wenwengu valuation engine. "
            "Run scripts/install_engine.py and try again."
        )

    return command, cwd


def auto_install_engine() -> Path:
    layout = detect_preferred_layout()
    sys.stderr.write(
        "未发现可用的 wenwengu 估值引擎，正在自动安装后继续执行。\n"
    )
    try:
        result = install_binary(layout=layout, force=False)
    except SystemExit as exc:
        message = str(exc).strip() or "unknown install error"
        raise SystemExit(
            "自动安装估值引擎失败。"
            f"详细原因: {message}。"
            "可以稍后手动运行 scripts/install_engine.py。"
        ) from exc

    installed_path = Path(result["binary_path"]).expanduser().resolve()
    sys.stderr.write(f"估值引擎已安装到 {installed_path}\n")
    return installed_path
